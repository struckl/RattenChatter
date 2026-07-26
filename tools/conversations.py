"""Conversation scripts for Ratten Chatter.

Each entry is one exchange on the radio net. `lines` is a list of
`(speaker, text, gap_before)` where:

  speaker     a key in cast.CAST
  text        what they say — write numbers as words ("two seven zero") so the
              TTS reads them like a pilot instead of like a calculator
  gap_before  seconds of dead air before this line. Ignored on the first line.
              0.3–0.8 is a snap answer, 1.0–2.0 is normal, 2.5+ is someone
              actually looking something up.

Shape rules, because this is what makes it sound like radio and not like a
sound pack:

  * TWO speakers per exchange, no more. Two aircraft, or an aircraft and a
    tower, or an aircraft and mission control. A third voice turns an overheard
    conversation into a scene, and the player stops flying and starts listening.
  * Two or three lines. One call, one answer, and at most one closing word.
  * They alternate. A, B, A — never two lines from the same person in a row.
  * Real transmissions are clipped. Not every line is a full sentence.
  * People step on themselves, correct themselves, and get bored. Leave the
    "uh", the "yeah", the half-repeated word in.
  * Not every exchange resolves. Some just stop.
  * Use the game's own vocabulary: Scythe and Scimitar for air-to-air, ARAD
    one sixteen for SEAD, StratoLance and Linebreaker for SAMs, Port Maris and
    Agrapol and Vigil Cay for geography.

`mood` is only documentation for humans reading this file.
"""

CONVERSATIONS = [
    # ------------------------------------------- aircraft and mission control
    dict(
        tag="checkin-razor",
        mood="routine",
        lines=[
            ("RAZOR ONE", "Magic, Razor one one, flight of two off North Boscali, passing eight thousand for two two zero.", 0),
            ("MAGIC", "Razor one one, Magic, radar contact. Picture is clean.", 1.1),
            ("RAZOR ONE", "Razor copies clean.", 0.8),
        ],
    ),
    dict(
        tag="picture-clean",
        mood="routine",
        lines=[
            ("VIPER ONE", "Magic, Viper, say the picture.", 0),
            ("MAGIC", "Nearest group two hundred miles north, cold. Nothing airborne south of the strait.", 1.6),
        ],
    ),
    dict(
        tag="handoff-warden",
        mood="routine",
        lines=[
            ("MAGIC", "Chisel one one, contact Warden on secondary. They own the western half tonight.", 0),
            ("CHISEL ONE", "Chisel switching. Thanks for the help, Magic.", 1.1),
            ("MAGIC", "Any time. Magic out.", 0.7),
        ],
    ),
    dict(
        tag="bandit-commit",
        mood="tense",
        lines=[
            ("MAGIC", "Razor, single group, zero four five for sixty, twenty thousand, hot.", 0),
            ("RAZOR ONE", "Razor one one committing.", 1.0),
            ("MAGIC", "Cleared to engage. Declare Revoker.", 1.2),
        ],
    ),
    dict(
        tag="defensive-vector",
        mood="tense",
        lines=[
            ("SABRE ONE", "Sabre one, defending! Flares, right hand turn, low!", 0),
            ("MAGIC", "Sabre, come left two two zero, descend. Terrain is your friend.", 1.3),
            ("SABRE ONE", "Two two zero, going down.", 1.0),
        ],
    ),
    dict(
        tag="no-joy-jamming",
        mood="tense",
        lines=[
            ("KESTREL ONE", "Magic, Kestrel one, no joy. Where is he?", 0),
            ("MAGIC", "Nose on, twelve miles, co-altitude. He should be on your radar.", 1.4),
            ("KESTREL ONE", "Nothing on the scope. I think there's a Medusa working me.", 1.7),
        ],
    ),
    dict(
        tag="clear-behind",
        mood="tense",
        lines=[
            ("DAGGER ONE", "Magic, Dagger flight egressing south. Request a picture behind us.", 0),
            ("MAGIC", "Dagger, nearest group thirty five miles, cold. You're clear.", 1.8),
        ],
    ),
    dict(
        tag="deconfliction",
        mood="routine",
        lines=[
            ("MAGIC", "Widow, be advised Hammer flight is working the same target area, four thousand and below.", 0),
            ("WIDOW ONE", "Widow copies. We'll stay above ten.", 1.5),
            ("MAGIC", "Appreciated.", 0.9),
        ],
    ),
    dict(
        tag="altitude-block",
        mood="routine",
        lines=[
            ("WARDEN", "Jackal, I need you out of the block. Descend and maintain one two thousand.", 0),
            ("JACKAL", "One two thousand, Jackal. Who's coming through?", 1.4),
            ("WARDEN", "Two Compasses with something heavy under the wings.", 1.6),
        ],
    ),
    dict(
        tag="medusa-jamming",
        mood="routine",
        lines=[
            ("GHOST", "Magic, Ghost is in the orbit. Jammers are hot on the eastern corridor.", 0),
            ("MAGIC", "Copy Ghost. Their search radars just went blind. Nice.", 2.0),
            ("GHOST", "I'll hold this station twenty minutes, then I need fuel.", 1.6),
        ],
    ),
    dict(
        tag="bda",
        mood="routine",
        lines=[
            ("WARDEN", "Widow, can you give me damage assessment on the vertical factory?", 0),
            ("WIDOW ONE", "North building is flat. South half is still standing and still working.", 3.6),
            ("WARDEN", "Copy. That's going back on the list.", 2.0),
        ],
    ),
    dict(
        tag="push-time",
        mood="tense",
        lines=[
            ("MAGIC", "Hammer, push time in two minutes. Confirm you're in position.", 0),
            ("HAMMER ONE", "Hammer flight, four ships, in position.", 1.3),
            ("MAGIC", "Good. Standing by.", 1.0),
        ],
    ),
    dict(
        tag="late-push",
        mood="tense",
        lines=[
            ("ANVIL ONE", "Magic, Anvil is, uh, we're going to be about ninety seconds late.", 0),
            ("MAGIC", "Anvil, understood. We'll hold the SEAD window open for you.", 1.7),
            ("ANVIL ONE", "Thanks. Pushing it up.", 1.2),
        ],
    ),
    dict(
        tag="launch-warning",
        mood="tense",
        lines=[
            ("MAGIC", "All players, StratoLance launch out of Harmony Sands. Multiple tracks northbound.", 0),
            ("SPADE", "Spade copies, going low.", 1.5),
        ],
    ),
    dict(
        tag="sead-emitter",
        mood="tense",
        lines=[
            ("HAMMER ONE", "Magic, Hammer one one, we're seeing a StratoLance emitter bearing one one zero.", 0),
            ("MAGIC", "Confirmed. That's the R nine site north of Sandrift, it came up two minutes ago.", 1.8),
            ("HAMMER ONE", "Hammer's in from the west with ARAD one sixteen.", 1.5),
        ],
    ),
    dict(
        tag="naval-strike",
        mood="tense",
        lines=[
            ("MAGIC", "Chisel, surface group confirmed. One Argus class frigate, two escorts, forty miles west of Vigil Cay.", 0),
            ("CHISEL ONE", "Chisel copies. We've got four ASHM three hundred between us.", 2.0),
            ("MAGIC", "Be aware the frigate is shooting. Recommend low ingress.", 1.7),
        ],
    ),
    dict(
        tag="ejection-chute",
        mood="grim",
        lines=[
            ("VIPER TWO", "Magic, Viper one is hit. I've got a good chute, one chute.", 0),
            ("MAGIC", "Copy one chute. Mark the position and hold overhead if you can.", 2.1),
            ("VIPER TWO", "Holding overhead at four thousand.", 1.4),
        ],
    ),
    dict(
        tag="sar-threat",
        mood="tense",
        lines=[
            ("LIFEGUARD", "Magic, Lifeguard one, five minutes from the survivor. Any threats?", 0),
            ("MAGIC", "There's a Linebreaker two miles east of you. Come in from the water.", 1.8),
            ("LIFEGUARD", "From the water, copy. Ninety seconds on the ground.", 1.5),
        ],
    ),
    dict(
        tag="missing-flight",
        mood="grim",
        lines=[
            ("WARDEN", "Ghost, do you have anything on Talon four?", 0),
            ("GHOST", "Negative. He was with me and then he wasn't.", 2.1),
            ("WARDEN", "Last radar hit was eight minutes ago over the strait.", 2.6),
        ],
    ),
    dict(
        tag="helo-lowlevel",
        mood="routine",
        lines=[
            ("LIFEGUARD", "Warden, Lifeguard one is low level up the valley, one hundred feet.", 0),
            ("WARDEN", "Lifeguard, copy. I'll lose you on radar in about a minute.", 1.9),
            ("LIFEGUARD", "Understood. We'll call you when we're back up.", 1.5),
        ],
    ),
    dict(
        tag="nuke-auth",
        mood="grim",
        lines=[
            ("KEYSTONE", "Darkreach one one, this is Keystone. Authenticate Whiskey Tango.", 0),
            ("PELICAN", "Keystone, Darkreach one one authenticates Whiskey Tango, uh, Delta Seven.", 2.5),
            ("KEYSTONE", "Correct. You are cleared to release. Target package two.", 2.8),
        ],
    ),
    dict(
        tag="nuke-aftermath",
        mood="grim",
        lines=[
            ("MAGIC", "All players, flash to the south east. Do not look at it. Expect datalink degradation.", 0),
            ("TUSK", "Tusk copies. God.", 2.4),
        ],
    ),
    dict(
        tag="rtb-quiet",
        mood="routine",
        lines=[
            ("SHEPHERD", "Magic, Shepherd is off station, returning to base.", 0),
            ("MAGIC", "Shepherd, radar contact lost, squawk standby. Good night.", 1.7),
            ("SHEPHERD", "Good night.", 1.2),
        ],
    ),
    dict(
        tag="shift-change",
        mood="routine",
        lines=[
            ("MAGIC", "Sentry, we're handing over the picture. Twelve friendly tracks, one unknown east of Ignus.", 0),
            ("SENTRY", "Sentry copies twelve and one unknown. We have the picture.", 2.3),
            ("MAGIC", "It's been quiet. Try to keep it that way.", 1.6),
        ],
    ),

    # -------------------------------------------------- aircraft and aircraft
    dict(
        tag="state-check",
        mood="routine",
        lines=[
            ("VIPER ONE", "Viper two, say state.", 0),
            ("VIPER TWO", "Four point two. No joy on the tanker yet.", 1.0),
            ("VIPER ONE", "He's twenty left of the track, thirty two thousand. Follow me through.", 1.3),
        ],
    ),
    dict(
        tag="splash",
        mood="tense",
        lines=[
            ("TALON FOUR", "Splash! Splash one, that's a kill, he's going down!", 0),
            ("TALON ONE", "Talon four, calm down and rejoin. Right two seven zero.", 1.5),
            ("TALON FOUR", "Two seven zero. Sorry.", 1.1),
        ],
    ),
    dict(
        tag="scythe-pair",
        mood="tense",
        lines=[
            ("WIDOW ONE", "Widow one, Scythe, Scythe.", 0),
            ("WIDOW TWO", "Two same, two away.", 0.9),
            ("WIDOW ONE", "Time of flight twelve seconds. Stay with me on the notch.", 1.3),
        ],
    ),
    dict(
        tag="reset-west",
        mood="tense",
        lines=[
            ("WIDOW ONE", "Both timed out. Reset west, Widow.", 0),
            ("WIDOW TWO", "Two's coming west.", 1.0),
        ],
    ),
    dict(
        tag="bugout",
        mood="tense",
        lines=[
            ("DAGGER ONE", "Dagger, bug out south, bug out south. We're out of missiles.", 0),
            ("DAGGER TWO", "Two's with you. Uh, two is spiked from the east.", 1.1),
            ("DAGGER ONE", "Just keep it low.", 1.2),
        ],
    ),
    dict(
        tag="tally-visual",
        mood="tense",
        lines=[
            ("VIPER TWO", "Viper one, tally one, low, crossing left to right.", 0),
            ("VIPER ONE", "Say the altitude.", 1.0),
            ("VIPER TWO", "Down in the weeds. Two thousand, maybe less.", 1.2),
        ],
    ),
    dict(
        tag="weapons-check",
        mood="routine",
        lines=[
            ("TALON ONE", "Talon four, what have you got left?", 0),
            ("TALON FOUR", "Two Scimitars and about half the gun.", 1.3),
            ("TALON ONE", "Alright. You're shooter, I'll cover.", 1.4),
        ],
    ),
    dict(
        tag="linebreaker-treeline",
        mood="tense",
        lines=[
            ("CHISEL TWO", "Chisel one, Linebreaker launcher in the treeline, south end of the bridge.", 0),
            ("CHISEL ONE", "Yeah, I see the smoke. Don't overfly it.", 1.3),
            ("CHISEL TWO", "Not planning on it.", 0.8),
        ],
    ),
    dict(
        tag="sam-shutdown",
        mood="routine",
        lines=[
            ("HAMMER THREE", "Emitter's down. He shut off when the missile got close.", 0),
            ("HAMMER ONE", "Of course he did. Mark the position, we'll come back with something dumber.", 1.6),
            ("HAMMER THREE", "Marked.", 1.0),
        ],
    ),
    dict(
        tag="sar-cover",
        mood="tense",
        lines=[
            ("LIFEGUARD", "Razor, Lifeguard one is going in. I'd like you overhead.", 0),
            ("RAZOR ONE", "Razor's got you covered. We'll be at three thousand.", 1.4),
        ],
    ),
    dict(
        tag="lost-wingman-wx",
        mood="tense",
        lines=[
            ("KESTREL TWO", "Kestrel one, I'm losing you in this. Going lost wingman.", 0),
            ("KESTREL ONE", "Copy. I'll turn left ten degrees and hold this altitude.", 1.4),
            ("KESTREL TWO", "Left ten, holding. Call me when you're out of it.", 1.5),
        ],
    ),
    dict(
        tag="banter-weather",
        mood="banter",
        lines=[
            ("RAZOR TWO", "Razor one, you seeing this weather over Port Maris?", 0),
            ("RAZOR ONE", "I'm seeing it. Forecast said scattered.", 1.4),
            ("RAZOR TWO", "Forecast says a lot of things.", 1.1),
        ],
    ),
    dict(
        tag="banter-formation",
        mood="banter",
        lines=[
            ("DAGGER ONE", "Dagger two, you're way out of position.", 0),
            ("DAGGER TWO", "I know, I know. My trim's fighting me.", 1.2),
            ("DAGGER ONE", "Blame the aircraft, sure.", 1.4),
        ],
    ),
    dict(
        tag="banter-food",
        mood="banter",
        lines=[
            ("COWBOY", "Stinger, any idea what they're serving back at Maris tonight?", 0),
            ("STINGER", "Same thing as last night.", 1.7),
            ("COWBOY", "That's what I was afraid of.", 1.2),
        ],
    ),
    dict(
        tag="banter-newguy",
        mood="banter",
        lines=[
            ("KESTREL ONE", "Kestrel two, that was a nice landing.", 0),
            ("KESTREL TWO", "Was it?", 1.1),
            ("KESTREL ONE", "No. But you walked away.", 1.4),
        ],
    ),
    dict(
        tag="radio-check",
        mood="routine",
        lines=[
            ("MOTH", "Spade, Moth. Radio check.", 0),
            ("SPADE", "Moth, you're weak but readable.", 1.7),
            ("MOTH", "Weak but readable. Story of my life.", 1.4),
        ],
    ),
    dict(
        tag="banter-long-day",
        mood="banter",
        lines=[
            ("SPADE", "Ghost, how long have you been on station?", 0),
            ("GHOST", "Long enough that I've started talking to myself.", 1.8),
            ("SPADE", "Yeah, we heard.", 1.5),
        ],
    ),
    dict(
        tag="banter-autopilot",
        mood="banter",
        lines=[
            ("SHEPHERD", "Tusk, is your autopilot holding altitude?", 0),
            ("TUSK", "Mine wanders about two hundred feet either way.", 1.5),
            ("SHEPHERD", "Same. So it's not just me.", 1.3),
        ],
    ),

    # ----------------------------------------------- aircraft and tower/field
    dict(
        tag="taxi-maris",
        mood="routine",
        lines=[
            ("BADGER", "Maris Ground, Badger one one, two Revokers at the north ramp, request taxi.", 0),
            ("MARIS GROUND", "Badger one one, taxi to runway zero nine via Bravo. Hold short.", 1.6),
            ("BADGER", "Zero nine via Bravo, hold short. Badger.", 1.0),
        ],
    ),
    dict(
        tag="takeoff-clearance",
        mood="routine",
        lines=[
            ("MARIS TOWER", "Badger one one, wind zero seven zero at fourteen, runway zero nine, cleared for takeoff.", 0),
            ("BADGER", "Cleared for takeoff, zero nine. Badger's rolling.", 1.2),
        ],
    ),
    dict(
        tag="min-fuel-landing",
        mood="tense",
        lines=[
            ("PELICAN", "Maris Tower, Pelican, ten miles south, one thousand four hundred pounds, request straight in.", 0),
            ("MARIS TOWER", "Pelican, you're number two behind a Compass. Can you hold?", 1.7),
            ("PELICAN", "Negative. I'd rather not.", 1.2),
        ],
    ),
    dict(
        tag="go-around",
        mood="routine",
        lines=[
            ("MARIS TOWER", "Tusk, go around, go around. Vehicle on the runway.", 0),
            ("TUSK", "Going around. Left closed traffic?", 1.0),
            ("MARIS TOWER", "Left closed traffic approved. Apologies, that was a wreck crew who did not hear me.", 1.5),
        ],
    ),
    dict(
        tag="gear-emergency",
        mood="tense",
        lines=[
            ("SANDRIFT TOWER", "Jackal, say the nature of your emergency.", 0),
            ("JACKAL", "Holes in the left wing, hydraulics dropping, and I'm not sure about the gear.", 1.5),
            ("SANDRIFT TOWER", "Roger. Emergency services are rolling. Runway one eight, cleared for the option.", 2.1),
        ],
    ),
    dict(
        tag="field-attacked",
        mood="tense",
        lines=[
            ("AGRAPOL TOWER", "Moth, the field is under attack. Do not enter the pattern.", 0),
            ("MOTH", "Moth copies. Diverting to the highway strip.", 1.5),
            ("AGRAPOL TOWER", "Negative, K ninety two is cratered. Try Vigil Cay.", 1.4),
        ],
    ),
    dict(
        tag="approach-traffic",
        mood="routine",
        lines=[
            ("OPAL APPROACH", "Shepherd, descend and maintain six thousand, expect the visual to two two.", 0),
            ("SHEPHERD", "Six thousand, visual two two, Shepherd.", 1.4),
            ("OPAL APPROACH", "And there's a Tarantula doing air work west of the field, four thousand.", 2.6),
        ],
    ),
    dict(
        tag="bird-strike",
        mood="routine",
        lines=[
            ("BADGER", "Maris Tower, Badger, I think I took a bird on the climb out. Engine looks fine.", 0),
            ("MARIS TOWER", "Badger, copy. Do you want to come back?", 2.0),
            ("BADGER", "Negative, continuing. I'll have them look at it after.", 1.7),
        ],
    ),
    dict(
        tag="runway-change",
        mood="routine",
        lines=[
            ("MARIS TOWER", "Spade, wind's swung round. Runway in use is now two seven.", 0),
            ("SPADE", "Two seven, Spade. I'll take the downwind.", 1.5),
            ("MARIS TOWER", "Report abeam.", 1.0),
        ],
    ),
    dict(
        tag="fuel-diversion",
        mood="tense",
        lines=[
            ("SHEPHERD", "Opal Approach, I'm not going to make Cliffline. Request Opal.", 0),
            ("OPAL APPROACH", "Shepherd, approved. Direct Opal, descend at your discretion.", 1.8),
            ("SHEPHERD", "Much appreciated.", 1.2),
        ],
    ),
    dict(
        tag="rearm-hold",
        mood="routine",
        lines=[
            ("MULE", "Maris Ground, Mule four, munitions truck to pad six, request crossing at Alpha.", 0),
            ("MARIS GROUND", "Mule four, hold at Alpha. I have a Darkreach taxiing behind you.", 1.7),
            ("MULE", "Holding at Alpha.", 1.0),
        ],
    ),

    # --------------------------------------------------- aircraft and tanker
    dict(
        tag="tanker-precontact",
        mood="routine",
        lines=[
            ("STINGER", "Texaco, Stinger, twenty miles in trail, request the boom.", 0),
            ("TEXACO", "Stinger, cleared to the observation position, precontact when ready. We're in a left turn.", 1.8),
            ("STINGER", "Stinger, precontact.", 3.0),
        ],
    ),
    dict(
        tag="tanker-disconnect",
        mood="routine",
        lines=[
            ("TEXACO", "Disconnect, disconnect. You drifted left.", 0),
            ("LONGBOW", "Yeah, my fault. Coming back to precontact.", 1.2),
            ("TEXACO", "No harm. Take your time, we're not going anywhere.", 1.5),
        ],
    ),
    dict(
        tag="tanker-priority",
        mood="tense",
        lines=[
            ("SABRE ONE", "Texaco, Sabre one, eight hundred pounds. I really need this.", 0),
            ("TEXACO", "Sabre, cleared straight to contact. Come on in.", 1.3),
            ("SABRE ONE", "Thank you.", 1.0),
        ],
    ),
    dict(
        tag="tanker-bored",
        mood="banter",
        lines=[
            ("COWBOY", "Texaco, how long have you been up here?", 0),
            ("TEXACO", "Uh... six hours? Seven. I've stopped counting.", 1.4),
            ("COWBOY", "Rough.", 1.1),
        ],
    ),
    dict(
        tag="tanker-track-move",
        mood="routine",
        lines=[
            ("TEXACO", "Longbow, we're moving the track twenty miles west. It's getting busy out here.", 0),
            ("LONGBOW", "Twenty west, copy. I'll find you.", 1.6),
        ],
    ),

    # -------------------------------------------------- aircraft and carrier
    dict(
        tag="carrier-charlie",
        mood="routine",
        lines=[
            ("KESTREL TWO", "Hyperion, Kestrel two, ten miles, state three point one, no ordnance.", 0),
            ("HYPERION", "Kestrel two, charlie on arrival. Deck is green, winds down the angle at twelve.", 1.9),
            ("KESTREL TWO", "Kestrel two, charlie.", 1.1),
        ],
    ),
    dict(
        tag="ball-call",
        mood="tense",
        lines=[
            ("KESTREL TWO", "Kestrel two, Vortex ball, two point one.", 0),
            ("PADDLES", "Roger ball, twelve knots. You're a little left.", 1.1),
            ("KESTREL TWO", "Correcting.", 1.0),
        ],
    ),
    dict(
        tag="waveoff",
        mood="tense",
        lines=[
            ("PADDLES", "You're high, you're high. Power off. Wave off, wave off!", 0),
            ("KESTREL TWO", "Waving off.", 0.8),
            ("PADDLES", "Come around, and this time fly the ball.", 2.3),
        ],
    ),
    dict(
        tag="deck-delay",
        mood="routine",
        lines=[
            ("HYPERION", "Kestrel two, we've got a foul deck. Hold at five miles, two thousand.", 0),
            ("KESTREL TWO", "Holding five miles, two thousand. How long?", 1.5),
            ("HYPERION", "Five minutes. Maybe less.", 1.8),
        ],
    ),
    dict(
        tag="ashm-warning",
        mood="tense",
        lines=[
            ("DYNAMO", "Viper, Dynamo. Inbound anti ship missiles, sea skimming, from the north west.", 0),
            ("VIPER ONE", "Viper copies. We'll stay outside five miles.", 1.6),
            ("DYNAMO", "Appreciated. Weapons are free inside that.", 1.4),
        ],
    ),
    dict(
        tag="good-night-ship",
        mood="routine",
        lines=[
            ("PELICAN", "Dynamo, Pelican is clear of your airspace, climbing out to the north.", 0),
            ("DYNAMO", "Pelican, copy clear. Safe flight.", 1.7),
        ],
    ),

    # ---------------------------------------------------- aircraft and ground
    dict(
        tag="nine-line-ready",
        mood="tense",
        lines=[
            ("SLEDGE", "Anvil one one, Sledge. You ready to copy?", 0),
            ("ANVIL ONE", "Anvil one one, ready to copy.", 1.1),
            ("SLEDGE", "Type two, bomb on coordinate. Dug in infantry with an AFV eight, tree line east of the crossroads.", 1.5),
        ],
    ),
    dict(
        tag="cleared-hot",
        mood="tense",
        lines=[
            ("ANVIL ONE", "Anvil one one, in from the south.", 0),
            ("SLEDGE", "Anvil one one, cleared hot.", 0.7),
            ("ANVIL ONE", "Off south.", 3.4),
        ],
    ),
    dict(
        tag="good-effect",
        mood="tense",
        lines=[
            ("SLEDGE", "Good effect, good effect. That's the AFV burning.", 0),
            ("ANVIL ONE", "Copy. Want me to come back around for the tree line?", 1.5),
            ("SLEDGE", "Affirm. Same run in.", 1.3),
        ],
    ),
    dict(
        tag="abort-friendlies",
        mood="tense",
        lines=[
            ("OUTLAW", "Abort, abort, abort. Friendlies moved into the target area.", 0),
            ("RHINO", "Rhino aborting. Coming off dry.", 0.9),
            ("OUTLAW", "Appreciate it. Hold high and dry, I'll re-attack you in five.", 1.5),
        ],
    ),
    dict(
        tag="danger-close",
        mood="tense",
        lines=[
            ("SLEDGE", "Anvil, this one's danger close, one hundred and fifty meters. I need your initials.", 0),
            ("ANVIL ONE", "Uh, Anvil acknowledges danger close. Initials Kilo Romeo.", 1.9),
            ("SLEDGE", "Kilo Romeo. Run in north to south, we're on the south side of the road.", 1.5),
        ],
    ),
    dict(
        tag="gun-run",
        mood="tense",
        lines=[
            ("SLEDGE", "Cowboy, no bombs left? Can you do anything with the gun?", 0),
            ("COWBOY", "I can make some noise. That usually moves them.", 1.6),
            ("SLEDGE", "Do it. Anything is better than nothing right now.", 1.4),
        ],
    ),
    dict(
        tag="wrong-net",
        mood="background",
        lines=[
            ("IRONHIDE", "Ironhide two, we are taking fire from the ridge, over.", 0),
            ("OUTLAW", "Ironhide, you're on the air support push. Switch to your company net.", 2.3),
            ("IRONHIDE", "Say again? You're breaking up.", 1.6),
        ],
    ),
    dict(
        tag="convoy-overhead",
        mood="routine",
        lines=[
            ("IRONHIDE", "Any air, Ironhide six. Escorting fuel trucks on the coast road, request an overhead look.", 0),
            ("RHINO", "Ironhide six, Rhino. I can give you ten minutes before I'm out of gas.", 2.1),
            ("IRONHIDE", "Ten minutes is ten minutes. Appreciate it.", 1.6),
        ],
    ),
    dict(
        tag="convoy-clear",
        mood="routine",
        lines=[
            ("RHINO", "Ironhide, road looks clear four miles ahead. Nothing moving.", 0),
            ("IRONHIDE", "Copy clear. That's the bit we were worried about.", 1.8),
        ],
    ),
    dict(
        tag="ground-waiting",
        mood="banter",
        lines=[
            ("MULE", "Ironhide, any word on when we're moving?", 0),
            ("IRONHIDE", "None. Sit tight.", 2.0),
            ("MULE", "Sitting tight. As always.", 1.6),
        ],
    ),
]
