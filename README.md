The roll20 5th edition OGL parses D20 rolls from the chat log of games using the 5th Edition OGL character sheet. <br/>
<br/>
The console version accepts the following arguments:<br/>
<br/>
HTML_FILE (required): The html chat log to parse. <br/>
n (required): Defines what type of dice to parse for. Ex: a D20 would be -n 20<br />
-a : The alias file that specifies what is a character or a player. It also attributes certain characters to players. It is explained in detail further on<br/>
-s : Defines what date to record rolls from. uses "month d, yyyy" format ex: November 5, 2018<br/>
--c : Continuation flag. For reasons explained below, rolls.py will store incomplete runs if a relationship file is not present. The --c flag allows a relationship file to be added in a second run without the data being recalculated. <br/>
--d : Debug flag. Will print some debug information like what dates were parsed <br />
--f : Forces a complete run without an alias file. Not recommended. <br />

<br/>
Run Types:<br/>
Because chat logs for games can be hundreds of thousands of lines long, execution time can be upwards of 10 seconds. To prevent duplicate runs in the event of a missing or incomplete relationship file, data is stored in data.dat. In the event of the continuation flag --c, data.dat will be used with the new relationship file. Incomplete runs are mostly to support the GUI edition of the Roll20 5th Edition OGL Parser. <br/>
<br/>
There are 3 run types:<br/><br />
COMPLETE FIRST RUN:<br/>
All files are present to do a complete run. Data is parsed, attributed and printed out to a csv<br/>
<br/>COMPLETE CONTINUATION<br/>
  Using the roll data stored in data.dat, data is attributed and printed out to a csv<br/>
<br />INCOMPLETE FIRST RUN:<br/>
  Rolls are parsed and printed out to data.dat<br/>
  <br/>
Format of data.dat:<br/>
name: [# of 1 rolls, # of 2 rolls, # of 3 rolls, ..., # of n rolls]<br/>
<br/>
where name is the author parsed from the chat log <br/>
<br/>
Format of the alias file<br/>
The alias file is broken into 5 sections seperated by a [$12] token.The sections are:<br/>
<br/>
(character aliases)<br/>
long_char=char<br/>
[$12]<br/>
(player aliases)<br/>
long_play=play<br/>
[$12]<br/>
(characters played by)<br/>
char=play<br/>
[$12]<br/>
(players list)<br/>
play,play2<br/>
[$12]<br/>
(character list)<br/>
char,char2<br/>
<br/>
For example, lets say we have John Doe who plays character Arogak Destel. We also have Jane who plays Enok. In the results file  we want to show the two characters Arogak and Enok (first names only). Likewise, we only want the first names of the players.<br/>
<br/>
Arogak Destel is then a character alias that needs to map to Arogak. John Doe -> John. Essentially the alias file sets up dictionary key value pairs. In the above situation the relationship file would be:<br/>
<br/>
Arogak Destel=Arogak<br/>
[$12]<br/>
John Doe=John<br/>
[$12]<br/>
Arogak=John<br/>
Enok=Jane<br/>
[$12]<br/>
John,Jane<br/>
[$12]<br/>
Arogak,Enok<br/>
<br/>
Note how Jane and Enok don't need aliases listed because their names are already in the desired form. <br/>
<br/>
If this all seems too complicated, check out the GUI executable version. <br/>
