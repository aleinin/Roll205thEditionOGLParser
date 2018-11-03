from bs4 import BeautifulSoup
import re
import csv
import math
import argparse

#CDF
def phi(x):
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

class RollWriter():
    xbar = -1
    varx = -1
    n = -1
    header = ""

    def calc_var(self):
        summation = 0
        squareation = 0
        for i in range(1, self.n + 1):
            summation += i
        self.xbar = summation / self.n
        for j in range(1, self.n + 1):
            squareation += (j - self.xbar) * (j - self.xbar)
        self.varx = squareation / (self.n - 1)

    def create_header(self):
        self.header = ["name", "Avg D20 Roll", "# Rolled", "Sum", "Expected Sum", "Variance", "st dev", "Difference",
                       "Z",
                       "P(Z>)", "Fair die?"]
        for i in range(1, self.n + 1):
            self.header.append(i)

    def write_all(self, file, play, n):
        self.players = play
        self.n = n
        self.create_header()
        with open(file, 'w', newline='') as out_file:
            self.calc_var()
            writer = csv.writer(out_file)
            self.write_characters(writer)
            writer.writerow([])
            self.write_people(writer)
            writer.writerow([])
            self.write_static(writer)

    def write_static(self, writer):
        writer.writerow(["Static Numbers"])
        writer.writerow(["Sides", "Prob", "Squared", "", ""])
        for i in range(1, self.n + 1):
            if i == 1:
                label = "XBar"
                calc = self.xbar
            elif i == 2:
                label = "S^2"
                calc = self.varx
            else:
                label = ""
                calc = ""
            writer.writerow([i, 1 / self.n, i * i, label, calc])

        # function that writes the characters. Characters are the names that are not people.
        # if the function cannot figure out who someone it will add it as a character. It will also
        # ask if that name "belongs" to anyone. This is equivalent to the played_by above.

    def write_characters(self, writer):
        writer.writerow(["Characters"])
        writer.writerow(self.header)
        char_rows = []
        # for all unique names found
        for character, list in character_rolls.items():
            roll_sum = 0
            dice_rolled = 0
            # list = a list of the occurences of each number being thrown
            # so for a D20 its [1 count, 2 count, 3count,..., 20 count]
            for i, roll in enumerate(list):
                # print("{} {}".format(i, roll))
                dice_rolled += roll
                roll_sum += (roll * (i + 1))
            avg = round((roll_sum / (dice_rolled * self.n)) * self.n, 3)
            # Name not specified in the dictionaries above
            # Expected (10.5*# Rolled) Sample Sum
            exp = dice_rolled * self.xbar
            # Sample variance
            var = dice_rolled * self.varx
            # sample standard deviation
            std = math.sqrt(var)
            # Expected Sum - Sample Sum
            diff = roll_sum - exp
            z = (roll_sum - exp) / std
            p = round((1 - phi(z)) * 100, 2)
            # 99% confidence interval
            if p > 99 or p < 1:
                conc = "unlikely"
            else:
                conc = "likely"
            char_rows.append([character, avg, dice_rolled, roll_sum, exp, var, std, diff, z, p, conc] + list)
        # sort by average D20
        char_rows.sort(key=lambda x: x[1])
        writer.writerows(char_rows)

    # function that writes the people. people are the names that are not characters.
    def write_people(self, writer):
        writer.writerow(["People"])
        writer.writerow(self.header)
        # total number of all dice thrown. Note, only includes people.
        # so if a character was thrown out via "" above, their rolls are not included in the total calculation
        all_dice_rolled = 0
        # Total sum
        all_sum = 0
        # total occurences of each D20 side
        all_list = []
        people_rows = []
        for person, list in person_rolls.items():
            roll_sum = 0
            dice_rolled = 0
            # list = a list of the occurences of each number being thrown
            # so for a D20 its [1 count, 2 count, 3count,..., 20 count]
            for i, roll in enumerate(list):
                # print("{} {}".format(i, roll))
                dice_rolled += roll
                roll_sum += (roll * (i + 1))
            avg = round((roll_sum / (dice_rolled * self.n)) * self.n, 3)
            exp = dice_rolled * self.xbar
            var = dice_rolled * self.varx
            std = math.sqrt(var)
            diff = roll_sum - exp
            z = (roll_sum - exp) / std
            p = round((1 - phi(z)) * 100, 2)
            if p > 95 or p < 5:
                conc = "unlikely"
            else:
                conc = "likely"
            people_rows.append([person, avg, dice_rolled, roll_sum] + [exp, var, std, diff, z, p, conc] + list)
            # summation work for total later
            all_dice_rolled = all_dice_rolled + dice_rolled
            all_sum = all_sum + roll_sum
            # all_list keeps track of the total occurences of eah D20 side
            if all_list == []:
                for i in range(0, self.n):
                    all_list.append(0)
            for i in range(0, self.n):
                all_list[i] += list[i]
        people_rows.sort(key=lambda x: x[1])
        writer.writerows(people_rows)
        # TOTAL
        avg = round(((all_sum / (all_dice_rolled * self.n)) * self.n), 3)
        exp = all_dice_rolled * self.xbar
        var = all_dice_rolled * self.varx
        std = math.sqrt(var)
        diff = all_sum - exp
        z = (all_sum - exp) / std
        p = round((1 - phi(z)) * 100, 2)
        if p > 95 or p < 5:
            conc = "unlikely"
        else:
            conc = "likely"
        writer.writerow(["Total", avg, all_dice_rolled, all_sum, exp, var, std, diff, z, p, conc] + all_list)
        prob_list = []
        for i in range(0, self.n):
            prob_list.append(0)
        for i in range(0, self.n):
            prob_list[i] = round(all_list[i] / all_dice_rolled, 3)
        writer.writerow(["", "", "", "", "", "", "", "", "", "", "Probability:"] + prob_list)


class RollParser():
    players = dict()
    recent_player = ""
    session = 1
    chk_sess = -1
    debug_set = set()
    debug_dates = dict()

    def get_type_of_dice(self, title):
        # title in form:
        # Rolling 1d20cs>20 + 5[DEX] + -3[MOD] + 3[PROF] = (<span class="basicdiceroll">5</span>)+5+-3+3
        # want to extract '1d20'
        num = ""
        type = ""
        pre = False
        post = False
        for char in title:
            if not post:
                if char != "d":
                    if char.isdigit():
                        num = num + char
                        pre = True
                    else:
                        if pre:
                            return -1, -1
                else:
                    post = True
            else:
                if char.isdigit():
                    type = type + char
                else:
                    break
        return int(num), int(type)

    def get_session(self, msg):
        parsed_date_line = msg.find("span", class_="tstamp")
        date = ""
        if parsed_date_line is not None:
            parsed_date = parsed_date_line.contents[0]
            date = re.sub(' [0-9]*:[0-9]*[A|P]M', "", parsed_date)
        else:
            parsed_date = ""
        if date not in self.debug_dates and date != "":
            self.debug_dates[date] = 1
        elif date != "":
            self.debug_dates[date] = self.debug_dates[date] + 1
        token = msg.find(text=re.compile(r'\[END S.\]'))
        if parsed_date == "July 27, 2018 1:33PM":
            self.session = 2
        elif parsed_date == "August 01, 2018 7:14PM":
            self.session = 3
        elif token is not None:
            self.session = int(token.replace("[END S", "").replace("]", ""))+1

    def get_roll_info(self, roll):
        try:
            title = roll['title']
            number_of_dice, type_of_dice = self.get_type_of_dice(title)
            if number_of_dice == -1:
                return -1, -1, -1
            else:
                num = ""
                post = False
                for char in title:
                    if not post:
                        if char == "=":
                            post = True
                    else:
                        if char != "+":
                            if char.isdigit():
                                num = num + char
                        else:
                            break
                try:
                    number_rolled = int(num)
                except ValueError:
                    print(title)
                    print(num)
                    quit()
            return number_of_dice, type_of_dice, number_rolled
        except KeyError:
            return -1, -1, -1

    def in_session(self):
        return self.session == self.chk_sess or self.chk_sess == -1

    def get_player_dn(self, file, n, chk_sess):
        self.chk_sess = chk_sess
        with open(file, 'r', encoding="utf8") as in_file:
            soup = BeautifulSoup(in_file, 'lxml')
            messages = soup.find_all("div", class_=re.compile(r'message.*'))
            for i, message in enumerate(messages):
                self.get_author(message)
                self.get_session(message)
                roll_cards = message.find("div", class_=re.compile(r'.*-simple|.*-atkdmg|.*-atk'))
                if roll_cards and self.in_session():
                    attacks = roll_cards.find_all("span", class_=re.compile(r'inlinerollresult.*'))
                    for roll in attacks:
                        number_of_dice, type_of_dice, number_rolled = self.get_roll_info(roll)
                        if type_of_dice == n:
                            if self.recent_player in self.players:
                                current_rolls = self.players[self.recent_player]
                                current_rolls[int(number_rolled) - 1] += 1
                                self.players[self.recent_player] = current_rolls
                                # otherwise create a new entry
                            else:
                                current_rolls = []
                                for i in range(1, 21):
                                    current_rolls.append(0)
                                current_rolls[int(number_rolled) - 1] += 1
                                self.players[self.recent_player] = current_rolls
        for date, occurence in self.debug_dates.items():
            print("{} with {} occurences".format(date, occurence))
        return self.players

    def get_author(self, tag):
        by = tag.find("span", class_="by")
        whisper = re.compile("^\(.*\)$")
        if by:
            self.recent_player = by.contents[0].replace(":", "").replace(" (GM)", "")
            if whisper.match(self.recent_player):
                self.recent_player = self.recent_player[1:-1].replace("From ", "")
            self.debug_set.add(self.recent_player)





def read_in_data():
    with open("data.dat", "r") as data_in:
        for line in data_in:
            line_split = line.split(":")
            name = line_split[0]
            rolls_str = line_split[1]
            rolls_str = rolls_str.replace("[", "").replace("]", "").replace(" ", "")
            rolls_split = rolls_str.split(",")
            rolls = []
            for roll in rolls_split:
                rolls.append(int(roll))
            data[name] = rolls


def attribute_data(relation_file):
    with open(relation_file, "r", encoding='utf-8-sig') as rfile:
        relations = rfile.read()
        subsections = relations.split("[$12]")
        for calias in subsections[0].split("\n"):
            if calias != "":
                half = calias.split("=")
                character_aliases[half[0]] = half[1]
        for alias in subsections[1].split("\n"):
            if alias != "":
                half = alias.split("=")
                aliases[half[0]] = half[1]
        for pby in subsections[2].split("\n"):
            if pby != "":
                half = pby.split("=")
                played_by[half[0]] = half[1]
        for ppl in subsections[3].replace("\n", "").split("="):
            if ppl != "":
                people.append(ppl)
    for name, rolls in data.items():
        if name in character_aliases:
            name = character_aliases[name]
        elif name in aliases:
            name = aliases[name]
        if name in people:
            if name in person_rolls:
                roll_data = person_rolls[name]
                for i in range(0, len(rolls)):
                    roll_data[i] += rolls[i]
                person_rolls[name] = roll_data
            else:
                person_rolls[name] = rolls
        else:
            if name in played_by:
                belongs_to = played_by[name]
                if belongs_to in person_rolls:
                    roll_data = person_rolls[belongs_to]
                    for i in range(0, len(rolls)):
                        roll_data[i] += rolls[i]
                        person_rolls[belongs_to] = roll_data
                else:
                    person_rolls[belongs_to] = rolls
            if name in character_rolls:
                roll_data = character_rolls[name]
                for i in range(0, len(rolls)):
                    roll_data[i] += rolls[i]
                    character_rolls[name] = roll_data
            else:
                character_rolls[name] = rolls

arg_parse = argparse.ArgumentParser()
arg_parse.add_argument("HTML_File", help="The HTML file to parse")
arg_parse.add_argument("-r", "-relationship", help="relationship file")
arg_parse.add_argument("--c", "--continue", help="continuation flag")
arg_parse.add_argument("-s", "-session", help="session to record for")
args = arg_parse.parse_args()
file_name = args.HTML_File

played_by = dict()
aliases = dict()
character_aliases = dict()
person_rolls = dict()
character_rolls = dict()
people = []

parser = RollParser()
data = dict()
if args.s:
    chk_sess = int(args.s)
else:
    chk_sess = -1

# COMPLETE FIRST RUN
if args.r and not args.c:
    data = parser.get_player_dn(file_name, 20, chk_sess)
    attribute_data(args.r)
    out = RollWriter()
    if chk_sess == -1:
        out.write_all("results.csv", data, 20)
    else:
        out.write_all("session_{}_results.csv".format(chk_sess), data, 20)
# COMPLETE CONTINUATION
elif args.r:
    read_in_data()
    attribute_data(args.r)
    out = RollWriter()
    if chk_sess == -1:
        out.write_all("results.csv", data, 20)
    else:
        out.write_all("session_{}_results.csv".format(chk_sess), data, 20)
# INCOMPLETE FIRST RUN
else:
    data = parser.get_player_dn(file_name, 20, chk_sess)
    with open("data.dat", 'w') as data_out:
        for key, val in data.items():
            print(key)
            data_out.write("{}:{}\n".format(key, val))
# "Chat Log for Tomb of Annihilation.html"  -r toarel.txt
# "Chat Log for Lost Mine of Phandelver.html" -r relationships.txt