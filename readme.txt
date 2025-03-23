# Autocomplete Name Extractor

## Author: Vedant

### Introduction
Hey there! This is my little project to wrangle every possible name out of an autocomplete API at `http://35.200.185.69:8000`. It’s got three versions—`v1`, `v2`, and `v3`—each spitting out its own quirky set of names. My mission? Grab them all, dodge rate limits like a pro, and dish out some cool stats about unique and repeated names across the versions.

### Approach
- **Prefix Exploration**: I used a trie (fancy tree thing) to dig through prefixes. It starts with single characters—like letters, numbers, even a dash or two—and keeps building longer prefixes when the API maxes out at 100 names.
- **Concurrency**: I’ve got 5 threads running wild (but controlled!) to chew through prefixes fast while keeping the API happy.
- **Rate Limiting**: When the API yells "429 Too Many Requests," I back off with some exponential time and retry.
- **Version Handling**: Each version gets its own name pile, and I crunch the numbers to see what’s unique, what’s repeated, and what’s everywhere.

### Features
- **Name Collection**: Sucks up all names from the API for `v1`, `v2`, and `v3`.
- **Statistics**: Spits out a juicy report with:
  - Total names per version.
  - How many API calls I made (a lot!).
  - Total unique names across the board.
  - Names that show up in just one version, two, or all three.
  - Repeated names (the social butterflies of the name world).
- **Output**: Dumps names into neat files: `names_v1.txt`, `names_v2.txt`, `names_v3.txt`.

### output
-INFO:root:
 Detailed Report:
 V1:
  Names Collected: 260
  API Calls: 40
 V2:
  Names Collected: 432
  API Calls: 40
 V3:
  Names Collected: 540
  API Calls: 40

 Total Names Collected (sum): 1232
 Total API Calls: 120
 Total Unique Names: 1231
 Names in Exactly One Version: 1230
 Names in Exactly Two Versions: 1
 Names in All Three Versions: 0
 Repeated Names (in more than one version): 1
 
Challenges and Learnings
Initial Testing: Oh man, the first test was a riot! I hit "run," sat back with popcorn, and… zilch. Nada. Dead silence. Turns out the API had been updated, and I was basically knocking on a ghost town’s door.  😂 
Prefix Coverage: Missed some names at first because I forgot digits. Added them to the mix, and boom—full coverage.
Thread Safety: Had to lock things down so my threads didn’t trip over each other. A small price for speed!
Conclusion
This was a blast—part scavenger hunt, part coding puzzle. It grabs all the names, juggles versions, and serves up stats like a champ. Plus, it taught me to double-check if the API’s alive before popping the confetti!