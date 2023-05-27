import json
import xml.etree.cElementTree as ET
import os.path

# Main files
localization_input = input('full path to the localization file (x/x/x/english.xml)')
dialog_file_input = input('full path to the dialog file (x/x/x/dialog.lsj)')
unpacked_data = input('full path to the UnpackedData folder (Gustav and Shared should be unpacked)')

localization = ET.parse(localization_input)
dialog_file = json.load(open(dialog_file_input))

write_file = dialog_file_input.split("\\")[-1].split(".")[0]


tav_handle = 'e0d1ff71-04a8-4340-ae64-9684d846eb83'
companions = {'3780c689-d903-41c2-bf64-1e6ec6a8e1e5': 'Astarion', '35c3caad-5543-4593-be75-e7deba30f062': 'Gale',
              'fb3bc4c3-49eb-4944-b714-d0cb357bb635': 'Laezel', '2bb39cf2-4649-4238-8d0c-44f62b5a3dfd': 'Shadowheart',
              'efc9d114-0296-4a30-b701-365fc07d44fb': 'Wyll'}

localization_root = localization.getroot()
dic_nodes = dialog_file['save']['regions']['dialog']['nodes'][0]['node']
dic_root_nodes = dialog_file['save']['regions']['dialog']['nodes'][0]['RootNodes']
dic_speakers = dialog_file['save']['regions']['dialog']['speakerlist'][0]['speaker']

# Characters names
glob_characters = ET.parse(unpacked_data + '/Gustav/Mods/Gustav/Globals/WLD_Main_A/Characters/_merged.lsx')
glob_characters_second = ET.parse(unpacked_data + '/Gustav/Mods/Gustav/Levels/WLD_Main_A/Characters/_merged.lsx')
root_template = ET.parse(unpacked_data + '/Gustav/Public/Gustav/RootTemplates/_merged.lsx')

# Tags and Flags
flags_folder = (unpacked_data + '/Gustav/Public/Gustav/Flags/')
shared_flags_folder = (unpacked_data + '/Shared/Public/Shared/Flags/')
tags_folder = (unpacked_data + '/Gustav/Public/Gustav/Tags/')
shared_tags_folder = (unpacked_data + '/Shared/Public/Shared/Tags/')
quest_tags_file = ET.parse(unpacked_data + '/Gustav/Mods/Gustav/Story/Journal/quest_prototypes.lsx')
class_tags_file = ET.parse(unpacked_data + '/Shared/Public/Shared/ClassDescriptions/ClassDescriptions.lsx')

approval_rating_folder = (unpacked_data + '/Gustav/Public/Gustav/ApprovalRatings/Reactions/')
difficulty_classes_file = ET.parse(unpacked_data + '/Shared/Public/Shared/DifficultyClasses/DifficultyClasses.lsx')

# Dicts
class_tags_dict = {}
quest_tags_dict = {}
difficulty_class_dic = {}

dialog_nodes_dict = {}
speakers_dict = {}
flags_dict = {}

lines_arr = []
root_nodes_uuid = []


class Dialog_Node(object):

    def __init__(self, node_index, uuid):
        self.node_index = node_index
        self.uuid = uuid
        self.speaker_index = ''
        self.speaker_name = ''
        self.line_handle = ''
        self.line_localization = ''
        self.checkflags = {}
        self.children = []
        self.jumptarget = ''
        self.constructor = ''
        self.is_end = False
        self.is_optional = False
        self.setflags = {}
        self.approval_rating_id = ''
        self.approval_rating = {}
        self.is_roll_succeed = None
        self.roll = None
        self.full_line = ''

    def set_speaker_name(self, dict):
        if self.speaker_index is not None:
            self.speaker_name = dict[str(self.speaker_index)].name
        else:
            self.speaker_name = None

        return self.speaker_name

    def set_flags_name(self, dict):
        for uuid in self.checkflags:
            self.checkflags[uuid] = dict[uuid].name
        for uuid in self.setflags:
            self.setflags[uuid] = dict[uuid].name

        if str(self.checkflags) == '{}':
            self.checkflags = None
        if str(self.setflags) == '{}':
            self.setflags = None

    def set_origins_names(self):
        names = {'REALLY_ASTARION': 'Astarion Origin', 'REALLY_SHADOWHEART': 'Shadowheart Origin',
                 'REALLY_WYLL': 'Wyll Origin', 'REALLY_LAEZEL': 'Laezel Origin', 'REALLY_KARLACH': 'Karlach Origin',
                 'REALLY_GALE': 'Gale Origin'}

        if self.speaker_name == 'Tav':
            if self.checkflags is not None:
                for value in self.checkflags.values():
                    if value in names.keys():
                        self.speaker_name = names[value]

        return self.speaker_name

    def print_roll(self):
        advantage = ''
        skill = ''
        difficulty = '0'
        if self.roll.advantage == '1':
            advantage = ', with Advantage'
        if self.roll.skill != '':
            skill = str(' (' + self.roll.skill + ')')
        if self.roll.difficulty is not None:
            difficulty = self.roll.difficulty
        roll = str('Roll: ' + self.roll.ability + skill + ' VS ' + difficulty + advantage)
        return roll

    def print_line(self):
        if self.line_localization is not None:
            self.full_line += '\n'
        if self.constructor == 'ActiveRoll':
            self.full_line += self.print_roll()
        if self.line_localization is not None:
            if self.speaker_name is not None:
                self.full_line += str(self.speaker_name) + ": " + str(self.line_localization)
            else:
                self.full_line += str(self.line_localization)

        if self.checkflags is not None:
            flags_line = ''
            for flag in self.checkflags.values():
                flags_line += str(flag) + ', '
            self.full_line += ' [' + flags_line[0:-2] + ']'

        if self.setflags is not None:
            flags_line = ''
            for flag in self.setflags.values():
                flags_line += str(flag) + ', '
            self.full_line += '\nSetFlags: ' + flags_line[0:-2]
        else:
            pass

        if self.approval_rating is not None:
            self.full_line += '\nApproval: ' + str(self.approval_rating)


class Speaker(object):
    def __init__(self, index, handle):
        self.index = index
        self.handle = handle
        self.name = None
        self.name_handle = None
        self.map_key = None
        self.template_name = None


class Flag(object):
    def __init__(self, check_set_type, type, uuid):
        self.check_set_type = check_set_type
        self.name = None
        self.type = type
        self.uuid = uuid


class Roll(object):
    def __init__(self, ability, difficulty, skill, advantage):
        self.ability = ability
        self.difficulty = difficulty
        self.skill = skill
        self.advantage = advantage


# creates dictionary {uuid: Dialog_Node (as Class obj)}
def set_nodes_list():
    iterator = 0
    for i in dic_nodes:
        uuid = i.get('UUID')
        dialog_nodes_dict[uuid['value']] = Dialog_Node(iterator, uuid['value'])
        iterator += 1
    return dialog_nodes_dict


# creates dictionary {index: Speaker (as Class obj)}
def set_speakers_list():
    for i in dic_speakers:
        char_index = i.get('index')['value']
        char_handle = i.get('list')['value']
        speakers_dict[char_index] = Speaker(char_index, char_handle)
    return speakers_dict


# searching for speakers names in files
def get_speaker_name(speaker):
    glob_character_templates = glob_characters.getroot().findall('region')[0][0][0]
    glob_character_second_templates = glob_characters_second.getroot().findall('region')[0][0][0]
    root_template_templates = root_template.getroot().findall('region')[0][0][0]
    handle = speaker.handle
    display_name = None
    template_name = None
    map_key = None

    # parse first file
    for game_objects in glob_character_templates:
        for attribute in game_objects:
            if 'DisplayName' in attribute.attrib.values():
                display_name = attribute.attrib.get('handle')
            if 'MapKey' in attribute.attrib.values():
                map_key = attribute.attrib.get('value')
            if 'TemplateName' in attribute.attrib.values():
                template_name = attribute.attrib.get('value')
        if map_key == handle:
            speaker.name_handle = display_name
            speaker.map_key = map_key
            speaker.template_name = template_name
            break
        else:
            display_name = None
            template_name = None
            map_key = None

    if speaker.name_handle is not None:
        pass
    else:
        # if name is None, parse second file
        for game_objects in glob_character_second_templates:
            for attribute in game_objects:
                if 'DisplayName' in attribute.attrib.values():
                    display_name = attribute.attrib.get('handle')
                if 'MapKey' in attribute.attrib.values():
                    map_key = attribute.attrib.get('value')
                if 'TemplateName' in attribute.attrib.values():
                    template_name = attribute.attrib.get('value')
            if map_key == handle:
                speaker.name_handle = display_name
                speaker.map_key = map_key
                speaker.template_name = template_name
                break
            else:
                display_name = None
                template_name = None
                map_key = None

    # if handle not in glob_character files
    # then parse RootTemplate
    if speaker.name_handle is not None:
        pass
    else:
        for game_objects in root_template_templates:
            for attribute in game_objects:
                if 'DisplayName' in attribute.attrib.values():
                    display_name = attribute.attrib.get('handle')
                if 'MapKey' in attribute.attrib.values():
                    map_key = attribute.attrib.get('value')
            if map_key == speaker.template_name:
                speaker.name_handle = display_name
            else:
                display_name = None
                map_key = None

    for line in localization_root:
        id = line.attrib.get('contentuid')
        if speaker.name_handle == id:
            speaker.name = line.text
            break
        if speaker.handle == tav_handle:
            speaker.name = 'Tav'

    return speaker


# assigned names to speakers class objects
def set_speakers():
    iterator = 1
    for speaker in speakers_dict.values():
        get_speaker_name(speaker)
        if speaker.name is None:
            speaker.name = 'Unknown Character ' + str(iterator)
    return speakers_dict


def get_root_nodes_uuid():
    for i in dic_root_nodes:
        root_node = i.get('RootNodes')
        root_nodes_uuid.append(root_node['value'])
    return root_nodes_uuid


def get_children(iterator):
    childrens_arr = []
    childrens = dic_nodes[iterator]['children'][0]
    if 'child' in childrens:
        for i in childrens['child']:
            childrens_arr.append(i['UUID'].get('value'))
    else:
        childrens_arr = None
    return childrens_arr


def get_constructor(iterator):
    constructor = dic_nodes[iterator]['constructor']['value']
    return constructor


def get_approval_rating_id(iterator):
    if 'ApprovalRatingID' in dic_nodes[iterator]:
        approval_rating_id = dic_nodes[iterator]['ApprovalRatingID']['value']
        return approval_rating_id


def get_jumptarget(iterator):
    jumptarget = dic_nodes[iterator]['jumptarget']['value']
    return jumptarget


def get_end_node(iterator):
    end = False
    if dic_nodes[iterator]['endnode'].get('value') is True:
        end = True
    return end


def get_roll_parameters(iterator):
    ability = dic_nodes[iterator]['Ability']['value']
    advantage = dic_nodes[iterator]['Advantage']['value']
    difficulty = difficulty_class_dic.get(dic_nodes[iterator]['DifficultyClassID']['value'])
    skill = dic_nodes[iterator]['Skill']['value']
    return Roll(ability, difficulty, skill, advantage)


def get_lines():
    # get handles
    temp_dic = {}
    for i in dic_nodes:
        TaggedTexts = i.get('TaggedTexts')
        Speaker = i.get('speaker')

        if TaggedTexts is not None:
            if 'TaggedText' in TaggedTexts[0]:
                handle = TaggedTexts[0]['TaggedText'][0]['TagTexts'][0]['TagText'][0]['TagText']['handle']
                temp_dic['handle'] = handle
                temp_dic['localization'] = None
        else:
            temp_dic['handle'] = None
            temp_dic['localization'] = None

        if Speaker is not None:
            temp_dic['speaker_index'] = Speaker['value']
            if int(temp_dic['speaker_index']) < 0:
                temp_dic['speaker_index'] = None
        else:
            temp_dic['speaker_index'] = None

        lines_arr.append(temp_dic)
        temp_dic = {}

    #get localization
    for i in lines_arr:
        for line in localization_root:
            id = line.attrib.get('contentuid')
            if i.get('handle') == id:
                i['localization'] = line.text

    return lines_arr


# parses class tags and creates dictionary {UUID: tag name}
def get_class_tag_dict():
    name = ''
    uuid = ''
    class_tags = class_tags_file.getroot().findall('region')[0][0][0]
    for classDescr in class_tags:
        for attribute in classDescr:
            if 'Name' in attribute.attrib.values():
                name = attribute.attrib.get('value')
            if 'UUID' in attribute.attrib.values():
                uuid = attribute.attrib.get('value')
        class_tags_dict[uuid] = name
    return class_tags_dict


# parses quest tags and creates dictionary {UUID: tag name}
def get_quest_tag_dict():
    quest_tags_root = quest_tags_file.getroot().findall('region')[0][0][0]
    guid = ''
    id = ''
    objective = ''
    for quest in quest_tags_root:
        steps = quest.findall('children')[0]
        for step in steps:
            for attribute in step:
                if 'DialogFlagGUID' in attribute.attrib.values():
                    guid = str(attribute.attrib.get('value'))
                if 'ID' in attribute.attrib.values():
                    id = str(attribute.attrib.get('value'))
                if 'Objective' in attribute.attrib.values():
                    objective = str(attribute.attrib.get('value'))
                quest_tags_dict[guid] = str(objective + ' (' + id + ')')
    return quest_tags_dict


# assigned flags and creates dictionary {UUID: Flag (as Class obj)}
def get_all_flags():
    for node in dic_nodes:
        uuid = node['UUID']['value']

        # get checkflags
        if 'flaggroup' in node['checkflags'][0]:
            flaggroup = node['checkflags'][0]['flaggroup']
            for flag in flaggroup:
                if len(flag['flag']) > 0:
                    for item in flag['flag']:
                        type = flag['type']['value']
                        item_uuid = item['UUID']['value']
                        dialog_nodes_dict.get(uuid).checkflags[item_uuid] = None
                        flags_dict[item_uuid] = Flag('checkflag', type, item_uuid)

            # get setflags
            if 'flaggroup' in node['setflags'][0]:
                flaggroup = node['setflags'][0]['flaggroup']
                for flag in flaggroup:
                    if len(flag['flag']) > 0:
                        for item in flag['flag']:
                            type = flag['type']['value']
                            item_uuid = item['UUID']['value']
                            dialog_nodes_dict.get(uuid).setflags[item_uuid] = None
                            flags_dict[item_uuid] = Flag('setflag', type, item_uuid)


# searching for flags names and assigned it to Flag class object
def flags_names():
    for flag in flags_dict:
        flag_file = flags_folder + str(flag) + '.lsx'
        shared_flag_file = shared_flags_folder + str(flag) + '.lsx'
        tag_file = tags_folder + str(flag) + '.lsx'
        shared_tag_file = shared_tags_folder + str(flag) + '.lsx'

        if flag in class_tags_dict:
            flags_dict[flag].name = class_tags_dict[flag]
            continue

        if flag in quest_tags_dict:
            flags_dict[flag].name = quest_tags_dict[flag]
            continue

        if os.path.exists(flag_file):
            file = ET.parse(flag_file)
            file_root = file.getroot()
            name = file_root.findall('region')[0][0][1].get('value')
            flags_dict[flag].name = name
            continue

        if os.path.exists(tag_file):
            file = ET.parse(tag_file)
            file_root = file.getroot()
            name = file_root.findall('region')[0][0][4].get('value')
            flags_dict[flag].name = name
            continue

        if os.path.exists(shared_tag_file):
            file = ET.parse(shared_tag_file)
            file_root = file.getroot()
            name = file_root.findall('region')[0][0][4].get('value')
            flags_dict[flag].name = name
            continue

        if os.path.exists(shared_flag_file):
            file = ET.parse(shared_flag_file)
            file_root = file.getroot()
            name = file_root.findall('region')[0][0][1].get('value')
            flags_dict[flag].name = name
            continue

        if flags_dict[flag].name is None:
            flags_dict[flag].name = 'Unknown Flag'


# parses approval rating and returned it as dic {companion name: rating}
def get_approval(node):
    approval_file = approval_rating_folder + str(node.approval_rating_id) + '.lsx'
    approval_dic = {}
    name = ''
    rating = ''
    if node.approval_rating_id is None:
        return
    else:
        if os.path.exists(approval_file):
            file = ET.parse(approval_file)
            file_root = file.getroot().findall('region')[0][0][0][0].findall('children')[0][0][0]
            for child in file_root:
                for attribute in child:
                    rating = '0'
                    if 'id' in attribute.attrib.values():
                        if attribute.attrib.get('value') in companions:
                            name = companions.get(attribute.attrib.get('value'))
                    if 'value' in attribute.attrib.values():
                        rating = attribute.attrib.get('value')

                    if rating != '0':
                        approval_dic[name] = rating
        return approval_dic


# parses roll DifficultyClasses and creates dictionary {UUID: difficulty}
def get_roll_difficulty_classes():
    difficulies = ''
    uuid = ''
    difficulty_classes = difficulty_classes_file.getroot().findall('region')[0][0][0]
    for d_class in difficulty_classes:
        for attribute in d_class:
            if 'Difficulties' in attribute.attrib.values():
                difficulies = attribute.attrib.get('value')
            if 'UUID' in attribute.attrib.values():
                uuid = attribute.attrib.get('value')
        difficulty_class_dic[uuid] = difficulies


def set_dialog_node_attributes():
    iterator = 0
    for node in dialog_nodes_dict.values():
        node.line_handle = lines_arr[iterator].get('handle')
        node.line_localization = lines_arr[iterator].get('localization')
        node.speaker_index = lines_arr[iterator].get('speaker_index')
        node.set_speaker_name(speakers_dict)
        node.children = get_children(iterator)
        node.constructor = get_constructor(iterator)
        node.is_end = get_end_node(iterator)
        if node.constructor == 'ActiveRoll':
            node.roll = get_roll_parameters(iterator)
        node.approval_rating_id = get_approval_rating_id(iterator)
        node.approval_rating = get_approval(node)
        node.set_flags_name(flags_dict)
        node.set_origins_names()

        iterator += 1


def print_dialog(root_nodes_uuid, dialog_nodes):
    visited_nodes = set()

    def dfs(node_uuid):
        node = dialog_nodes[node_uuid]
        node.print_line()
        if node.is_end is True:
            print("\nEnd")
        if node_uuid in visited_nodes:
            return
        visited_nodes.add(node_uuid)

        if node.children is not None:
            for child_uuid in node.children:
                dfs(child_uuid)
        else:
            print("\n------------------",end='')

    for root_uuid in root_nodes_uuid:
        print("Start", end='')
        dfs(root_uuid)


def write_dialog(root_nodes_uuid, dialog_nodes):
    visited_nodes = set()

    w_file = open(write_file + '.txt', 'w', encoding="utf-8")

    def dfs(node_uuid):
        node = dialog_nodes[node_uuid]
        node.print_line()
        line = node.full_line
        w_file.write(line)
        if node.is_end is True:
            w_file.write("\nEnd")
        if node_uuid in visited_nodes:
            return
        visited_nodes.add(node_uuid)

        if node.children is not None:
            for child_uuid in node.children:
                dfs(child_uuid)
        else:
            w_file.write("\n------------------\n")

    for root_uuid in root_nodes_uuid:
        w_file.write("Start")
        dfs(root_uuid)


get_class_tag_dict()
get_quest_tag_dict()

get_roll_difficulty_classes()

set_nodes_list()
set_speakers_list()
set_speakers()

get_all_flags()
flags_names()

get_lines()

get_root_nodes_uuid()

set_dialog_node_attributes()

write_dialog(root_nodes_uuid, dialog_nodes_dict)



''''
проверка роллов
constructor = ActiveRoll
constructor = RollResult, Success = true/false

переделать словарь лайнов в классы
'''''