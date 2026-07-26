"""Conversation scripts for Ratten Chatter.

Each entry is one exchange on the radio net. `lines` is a list of
`(speaker, text, gap_before)` where:

  speaker     a key in cast.CAST
  text        what they say — write numbers as words ("two seven zero") so the
              TTS reads them like a pilot instead of like a calculator
  gap_before  seconds of dead air before this line. Ignored on the first line.
              0.3–0.8 is a snap answer, 1.0–2.0 is normal, 2.5+ is someone
              actually looking something up.

Style rules that keep these from sounding like a phrasebook:
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
    # ---------------------------------------------------------------- routine
    dict(
        tag="checkin-razor",
        mood="routine",
        lines=[
            ("RAZOR ONE", "Magic, Razor one one, flight of two off North Boscali, passing eight thousand for two two zero.", 0),
            ("MAGIC", "Razor one one, Magic, radar contact. Picture is clean, closest group two hundred miles north, cold.", 1.1),
            ("RAZOR ONE", "Razor copies clean.", 0.9),
        ],
    ),
    dict(
        tag="handoff-warden",
        mood="routine",
        lines=[
            ("MAGIC", "Chisel one one, Magic. Contact Warden on secondary, they own the western half tonight.", 0),
            ("CHISEL ONE", "Chisel switching. Thanks for the help, Magic.", 1.0),
            ("MAGIC", "Any time. Magic out.", 0.7),
            ("CHISEL ONE", "Warden, Chisel one one, flight of two, level two four zero, checking in.", 3.4),
            ("WARDEN", "Chisel one one, Warden, loud and clear. I have you sweet on datalink.", 1.4),
        ],
    ),
    dict(
        tag="boredom-tanker",
        mood="banter",
        lines=[
            ("COWBOY", "Texaco, Cowboy. How long have you been up here?", 0),
            ("TEXACO", "Uh... six hours? Seven. I've stopped counting.", 1.3),
            ("COWBOY", "Rough.", 1.0),
            ("TEXACO", "We've got two thermoses and a crossword. We're fine.", 0.8),
        ],
    ),
    dict(
        tag="fuel-check",
        mood="routine",
        lines=[
            ("VIPER ONE", "Viper two, say state.", 0),
            ("VIPER TWO", "Four point two, no joy on the tanker yet.", 1.0),
            ("VIPER ONE", "Copy. He's twenty left of the track, thirty two thousand. I've got him on the pod.", 1.2),
            ("VIPER TWO", "Yeah, tally. Following you through.", 1.5),
        ],
    ),

    # ------------------------------------------------------------ air-to-air
    dict(
        tag="bandit-intercept",
        mood="tense",
        lines=[
            ("MAGIC", "Razor, single group, zero four five for sixty, twenty thousand, hot. Declare Revoker.", 0),
            ("RAZOR ONE", "Razor one one committing. Razor two, take the lead trail, I'll take the west side.", 1.2),
            ("RAZOR TWO", "Two.", 0.6),
            ("RAZOR ONE", "Scimitar away — Razor one one, Scimitar, single group.", 2.6),
            ("MAGIC", "Razor one one, your target maneuvering, dropping. Twenty four miles.", 2.2),
        ],
    ),
    dict(
        tag="splash-callout",
        mood="tense",
        lines=[
            ("TALON FOUR", "Splash! Splash one, that's a kill, he's going down!", 0),
            ("TALON ONE", "Talon four, calm down and rejoin. Right two seven zero.", 1.4),
            ("TALON FOUR", "Two seven zero, copy. Sorry.", 1.1),
        ],
    ),
    dict(
        tag="merge-defensive",
        mood="tense",
        lines=[
            ("SABRE ONE", "Sabre one, defending! Flares, right hand turn, low!", 0),
            ("MAGIC", "Sabre one, threat is at your six, three miles, closing.", 1.2),
            ("SABRE ONE", "I know! I know. Give me a heading out of here.", 1.0),
            ("MAGIC", "Come left two two zero, descend, terrain is your friend.", 1.1),
        ],
    ),
    dict(
        tag="no-joy",
        mood="tense",
        lines=[
            ("KESTREL ONE", "Magic, Kestrel one, no joy. Where is he?", 0),
            ("MAGIC", "Kestrel, bandit is nose on, twelve miles, co-altitude. He should be on your radar.", 1.3),
            ("KESTREL ONE", "Nothing on the scope. I think he's got a Medusa working him.", 1.6),
            ("MAGIC", "Confirmed, we're seeing jamming on that line. Recommend you go visual.", 2.0),
        ],
    ),
    dict(
        tag="scythe-shot",
        mood="tense",
        lines=[
            ("WIDOW ONE", "Widow one, Scythe, Scythe.", 0),
            ("WIDOW TWO", "Widow two same, two away.", 1.0),
            ("WIDOW ONE", "Time of flight twelve seconds. Stay with me on the notch.", 1.3),
            ("WIDOW TWO", "In the notch.", 2.8),
            ("WIDOW ONE", "Both timed out. Reset west, Widow.", 3.2),
        ],
    ),
    dict(
        tag="bugout",
        mood="tense",
        lines=[
            ("DAGGER ONE", "Dagger, bug out south, bug out south. We're out of missiles.", 0),
            ("DAGGER TWO", "Two's coming with you. Uh, two is spiked from the east.", 1.1),
            ("DAGGER ONE", "Just keep it low. Magic, Dagger flight egressing, request a picture behind us.", 1.5),
            ("MAGIC", "Dagger, nearest group thirty five miles, cold. You're clear.", 1.8),
        ],
    ),

    # ------------------------------------------------------------------ SEAD
    dict(
        tag="sead-stratolance",
        mood="tense",
        lines=[
            ("HAMMER ONE", "Magic, Hammer one one, we're seeing a StratoLance emitter bearing one one zero.", 0),
            ("MAGIC", "Hammer, confirmed. That's the R nine site north of Sandrift. It came up two minutes ago.", 1.6),
            ("HAMMER ONE", "Hammer one one is in from the west with ARAD one sixteen. Two ships.", 1.4),
            ("HAMMER THREE", "Three's in, thirty seconds behind.", 1.0),
        ],
    ),
    dict(
        tag="sam-shutdown",
        mood="routine",
        lines=[
            ("HAMMER THREE", "Emitter's down. He shut off when the missile got close.", 0),
            ("HAMMER ONE", "Of course he did. Mark the position, we'll come back with something dumber.", 1.5),
            ("HAMMER THREE", "Marked.", 1.0),
        ],
    ),
    dict(
        tag="sam-launch-warning",
        mood="tense",
        lines=[
            ("MAGIC", "All players, all players, StratoLance launch out of Harmony Sands. Multiple tracks northbound.", 0),
            ("SPADE", "Spade copies, going low.", 1.4),
            ("GHOST", "Ghost is descending. That thing reaches further than they told us.", 1.1),
            ("MAGIC", "Everybody below five thousand until it goes cold.", 1.7),
        ],
    ),
    dict(
        tag="linebreaker-callout",
        mood="tense",
        lines=[
            ("CHISEL TWO", "Chisel one, I've got a Linebreaker launcher in the treeline, south end of the bridge.", 0),
            ("CHISEL ONE", "Yeah, I see the smoke. Don't overfly it.", 1.2),
            ("CHISEL TWO", "Not planning on it.", 0.8),
        ],
    ),

    # -------------------------------------------------------------------- CAS
    dict(
        tag="cas-nine-line",
        mood="tense",
        lines=[
            ("SLEDGE", "Anvil one one, Sledge. You ready to copy?", 0),
            ("ANVIL ONE", "Anvil one one, ready to copy.", 1.1),
            ("SLEDGE", "Type two, bomb on coordinate. Target is dug in infantry with an AFV eight, tree line east of the crossroads.", 1.4),
            ("ANVIL ONE", "Copy, tree line east of the crossroads. I'll need a mark.", 2.2),
            ("SLEDGE", "Mark's out now. White smoke.", 1.6),
        ],
    ),
    dict(
        tag="cas-cleared-hot",
        mood="tense",
        lines=[
            ("ANVIL ONE", "Anvil one one, in from the south.", 0),
            ("SLEDGE", "Anvil one one, cleared hot.", 0.7),
            ("ANVIL ONE", "Off south.", 3.6),
            ("SLEDGE", "Good effect, good effect. That's the AFV burning. Come back around for the tree line.", 2.4),
        ],
    ),
    dict(
        tag="cas-abort",
        mood="tense",
        lines=[
            ("OUTLAW", "Abort, abort, abort. Friendlies moved into the target area.", 0),
            ("RHINO", "Rhino aborting, weapon is safe, coming off dry.", 0.9),
            ("OUTLAW", "Appreciate it. Hold high and dry, I'll re-attack you in five.", 1.4),
        ],
    ),
    dict(
        tag="danger-close",
        mood="tense",
        lines=[
            ("SLEDGE", "Anvil, this one's danger close, one hundred and fifty meters. I need your initials.", 0),
            ("ANVIL ONE", "Uh, Anvil one one acknowledges danger close. Initials Kilo Romeo.", 1.8),
            ("SLEDGE", "Kilo Romeo, copy. Make your run north to south, we're on the south side of the road.", 1.5),
        ],
    ),
    dict(
        tag="ground-net-bleed",
        mood="background",
        lines=[
            ("IRONHIDE", "Ironhide two, Ironhide two, we are taking fire from the ridge, over.", 0),
            ("OUTLAW", "Say again, all after the ridge.", 2.4),
            ("IRONHIDE", "From the ridge line, east of us. Two vehicles at least. We need something up here.", 1.5),
            ("OUTLAW", "Ironhide, you're on the air support push. Switch to your company net and I'll pass it along.", 2.0),
        ],
    ),

    # ----------------------------------------------------------- tower / field
    dict(
        tag="taxi-maris",
        mood="routine",
        lines=[
            ("BADGER", "Maris Ground, Badger one one, two Revokers at the north ramp, request taxi.", 0),
            ("MARIS GROUND", "Badger one one, taxi to runway zero nine via Bravo. Hold short.", 1.5),
            ("BADGER", "Zero nine via Bravo, hold short. Badger.", 1.0),
        ],
    ),
    dict(
        tag="takeoff-clearance",
        mood="routine",
        lines=[
            ("MARIS TOWER", "Badger one one, wind zero seven zero at fourteen, runway zero nine, cleared for takeoff.", 0),
            ("BADGER", "Cleared for takeoff, zero nine. Badger one one, rolling.", 1.2),
        ],
    ),
    dict(
        tag="landing-fuel-state",
        mood="tense",
        lines=[
            ("PELICAN", "Maris Tower, Pelican, ten miles south, one thousand four hundred pounds, request straight in.", 0),
            ("MARIS TOWER", "Pelican, you're number two behind a Compass on final. Can you hold?", 1.6),
            ("PELICAN", "Negative. I'd rather not.", 1.2),
            ("MARIS TOWER", "Understood. Pelican, cleared to land runway two seven, I'll send the Compass around.", 1.4),
        ],
    ),
    dict(
        tag="go-around",
        mood="routine",
        lines=[
            ("MARIS TOWER", "Tusk, go around, go around. Vehicle on the runway.", 0),
            ("TUSK", "Going around. Tusk.", 0.8),
            ("MARIS TOWER", "Apologies. That's a wreck removal crew who did not hear me.", 2.2),
            ("TUSK", "It happens. Left closed traffic?", 1.5),
            ("MARIS TOWER", "Left closed traffic approved.", 0.9),
        ],
    ),
    dict(
        tag="battle-damage",
        mood="tense",
        lines=[
            ("SANDRIFT TOWER", "Jackal, say the nature of your emergency.", 0),
            ("JACKAL", "I've got holes in the left wing, hydraulics are dropping, and I'm not sure about the gear.", 1.4),
            ("SANDRIFT TOWER", "Jackal, roger. Emergency services are rolling. Runway one eight, you're cleared for the option.", 2.0),
            ("JACKAL", "Copy. If the gear doesn't come down I'm going to put it in the dirt beside the runway.", 2.2),
            ("SANDRIFT TOWER", "Understood. We'll be there.", 1.6),
        ],
    ),
    dict(
        tag="airfield-attack",
        mood="tense",
        lines=[
            ("AGRAPOL TOWER", "All aircraft Agrapol, the field is under attack. Do not enter the pattern.", 0),
            ("MOTH", "Moth copies. Diverting to the highway strip.", 1.5),
            ("AGRAPOL TOWER", "Moth, negative, K ninety two is cratered. Try Vigil Cay.", 1.3),
            ("MOTH", "Vigil Cay. Yeah. Moth is going east.", 1.8),
        ],
    ),
    dict(
        tag="cross-country",
        mood="routine",
        lines=[
            ("OPAL APPROACH", "Shepherd, Opal Approach, descend and maintain six thousand, expect the visual to two two.", 0),
            ("SHEPHERD", "Six thousand, visual two two, Shepherd.", 1.3),
            ("OPAL APPROACH", "And Shepherd, be advised there's a Tarantula doing air work west of the field, four thousand.", 2.8),
            ("SHEPHERD", "Copy, looking.", 1.1),
        ],
    ),

    # ---------------------------------------------------------------- tanker
    dict(
        tag="tanker-rejoin",
        mood="routine",
        lines=[
            ("STINGER", "Texaco, Stinger, twenty miles in trail, request the boom.", 0),
            ("TEXACO", "Stinger, Texaco, cleared to the observation position, precontact when ready. We're in a left hand turn.", 1.7),
            ("STINGER", "Stinger, precontact.", 3.0),
            ("TEXACO", "Contact. Taking fuel.", 1.2),
        ],
    ),
    dict(
        tag="tanker-disconnect",
        mood="routine",
        lines=[
            ("TEXACO", "Disconnect, disconnect. You drifted left.", 0),
            ("LONGBOW", "Yeah, my fault. Coming back to precontact.", 1.2),
            ("TEXACO", "No harm. Take your time, we're not going anywhere.", 1.4),
        ],
    ),
    dict(
        tag="tanker-priority",
        mood="tense",
        lines=[
            ("TEXACO", "Longbow, break off, break off. I've got a Revoker inbound at bingo.", 0),
            ("LONGBOW", "Longbow's clear right.", 0.8),
            ("SABRE ONE", "Texaco, Sabre one, eight hundred pounds. I really need this.", 1.3),
            ("TEXACO", "Sabre, you're cleared straight to contact. Come on in.", 1.2),
        ],
    ),

    # ------------------------------------------------------------------ naval
    dict(
        tag="carrier-inbound",
        mood="routine",
        lines=[
            ("KESTREL TWO", "Hyperion, Kestrel two, ten miles, state three point one, no ordnance.", 0),
            ("HYPERION", "Kestrel two, Hyperion, charlie on arrival. Deck is green, winds down the angle at twelve.", 1.8),
            ("KESTREL TWO", "Kestrel two, charlie.", 1.1),
        ],
    ),
    dict(
        tag="carrier-wave-off",
        mood="tense",
        lines=[
            ("PADDLES", "You're high, you're high. Power off. Power off!", 0),
            ("PADDLES", "Wave off, wave off, foul deck!", 1.5),
            ("KESTREL TWO", "Waving off.", 0.7),
            ("PADDLES", "Kestrel, that was ugly. Come around, and this time fly the ball.", 2.4),
        ],
    ),
    dict(
        tag="naval-ashm",
        mood="tense",
        lines=[
            ("DYNAMO", "All aircraft, Dynamo. We have inbound anti ship missiles, sea skimming, from the north west.", 0),
            ("DYNAMO", "Do not overfly the task group. Weapons are free inside five miles.", 2.1),
            ("VIPER ONE", "Viper copies, staying outside.", 1.4),
            ("WIDOW ONE", "Widow one, understood. Good luck down there.", 1.2),
        ],
    ),
    dict(
        tag="naval-strike-brief",
        mood="tense",
        lines=[
            ("MAGIC", "Chisel, Magic. Surface group confirmed, one Argus class frigate and two escorts, forty miles west of Vigil Cay.", 0),
            ("CHISEL ONE", "Chisel copies. We've got four ASHM three hundred between us.", 1.9),
            ("MAGIC", "Understood. Be aware the frigate is shooting. Recommend a low ingress and pop.", 1.6),
            ("CHISEL ONE", "Yeah. That's the plan.", 1.5),
        ],
    ),

    # -------------------------------------------------------- rescue / losses
    dict(
        tag="ejection",
        mood="grim",
        lines=[
            ("VIPER TWO", "Viper one is hit, Viper one is hit! He's on fire, left side!", 0),
            ("VIPER TWO", "Magic, I've got a good chute. Repeat, good chute, one chute.", 2.4),
            ("MAGIC", "Copy one chute. Mark the position and hold overhead if you can.", 2.0),
            ("VIPER TWO", "Holding overhead. I'm at four thousand.", 1.4),
        ],
    ),
    dict(
        tag="sar-pickup",
        mood="tense",
        lines=[
            ("LIFEGUARD", "Magic, Lifeguard one, we're five minutes from the survivor position. Any threats?", 0),
            ("MAGIC", "Lifeguard, there's a Linebreaker two miles east of you. Come in from the water.", 1.7),
            ("LIFEGUARD", "From the water, copy. We'll be on the ground for ninety seconds.", 1.5),
            ("MAGIC", "Understood. Razor flight is overhead for you.", 1.6),
            ("RAZOR ONE", "Razor's got you covered, Lifeguard.", 1.2),
        ],
    ),
    dict(
        tag="missing-flight",
        mood="grim",
        lines=[
            ("WARDEN", "Ghost, Warden. Do you have anything on Talon four?", 0),
            ("GHOST", "Negative. He was with me and then he wasn't.", 2.0),
            ("WARDEN", "Last radar hit was eight minutes ago over the strait.", 2.6),
            ("GHOST", "Yeah.", 2.2),
        ],
    ),

    # ----------------------------------------------------------------- banter
    dict(
        tag="banter-weather",
        mood="banter",
        lines=[
            ("RAZOR TWO", "Razor one, you seeing this weather over Port Maris?", 0),
            ("RAZOR ONE", "I'm seeing it. Forecast said scattered.", 1.3),
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
            ("DAGGER TWO", "I will, actually.", 1.0),
        ],
    ),
    dict(
        tag="banter-food",
        mood="banter",
        lines=[
            ("COWBOY", "Anybody know what they're serving back at Maris tonight?", 0),
            ("STINGER", "Same thing as last night.", 1.6),
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
        tag="banter-radio-check",
        mood="routine",
        lines=[
            ("MOTH", "Anybody up on this push? Radio check.", 0),
            ("SPADE", "Moth, Spade, you're weak but readable.", 1.8),
            ("MOTH", "Weak but readable. Story of my life.", 1.4),
        ],
    ),

    # ----------------------------------------------------------- logistics/EW
    dict(
        tag="medusa-jamming",
        mood="routine",
        lines=[
            ("GHOST", "Magic, Ghost is in the orbit, jammers are hot on the eastern corridor.", 0),
            ("MAGIC", "Copy Ghost. We're seeing the effect, their search radars just went blind. Nice.", 1.9),
            ("GHOST", "I'll hold this station for twenty minutes, then I need fuel.", 1.7),
        ],
    ),
    dict(
        tag="rearm-request",
        mood="routine",
        lines=[
            ("MULE", "Maris Ground, Mule four, munitions truck heading to pad six, request crossing at Alpha.", 0),
            ("MARIS GROUND", "Mule four, hold at Alpha. I have a Darkreach taxiing behind you.", 1.6),
            ("MULE", "Holding at Alpha.", 1.0),
        ],
    ),
    dict(
        tag="convoy-escort",
        mood="routine",
        lines=[
            ("IRONHIDE", "Any air, any air, this is Ironhide six. We're escorting fuel trucks on the coast road, request an overhead look.", 0),
            ("RHINO", "Ironhide six, Rhino, I can give you ten minutes before I'm out of gas.", 2.0),
            ("IRONHIDE", "Ten minutes is ten minutes. Appreciate it.", 1.6),
        ],
    ),
    dict(
        tag="bda-request",
        mood="routine",
        lines=[
            ("WARDEN", "Widow, Warden. Can you give me damage assessment on the vertical factory?", 0),
            ("WIDOW ONE", "Stand by, we're coming back over the top.", 1.5),
            ("WIDOW ONE", "Warden, the north building is flat. South half is still standing and still working.", 4.2),
            ("WARDEN", "Copy, north flat, south intact. That's going back on the list.", 2.0),
        ],
    ),

    # ------------------------------------------------------------- the big one
    dict(
        tag="nuclear-authorization",
        mood="grim",
        lines=[
            ("KEYSTONE", "Darkreach one one, this is Keystone. Authenticate Whiskey Tango.", 0),
            ("PELICAN", "Keystone, Darkreach one one authenticates Whiskey Tango, uh, Delta Seven.", 2.4),
            ("KEYSTONE", "Correct. Darkreach one one, you are cleared to release. Target package two. Acknowledge.", 2.8),
            ("PELICAN", "Darkreach one one acknowledges. Cleared to release, package two.", 3.0),
        ],
    ),
    dict(
        tag="nuclear-aftermath",
        mood="grim",
        lines=[
            ("MAGIC", "All players, all players. Flash to the south east. Do not look at it.", 0),
            ("MAGIC", "Expect datalink degradation. Steer clear of the cloud.", 2.6),
            ("SPADE", "Spade copies.", 2.0),
            ("TUSK", "Tusk copies. God.", 1.8),
        ],
    ),
    dict(
        tag="strike-package-push",
        mood="tense",
        lines=[
            ("MAGIC", "All strike aircraft, push time is in two minutes. Confirm you're in position.", 0),
            ("HAMMER ONE", "Hammer flight, four ships, in position.", 1.4),
            ("CHISEL ONE", "Chisel, two ships, ready.", 1.0),
            ("ANVIL ONE", "Anvil, uh, we're going to be about ninety seconds late.", 1.3),
            ("MAGIC", "Anvil, understood, we'll hold the SEAD window open for you.", 1.7),
        ],
    ),

    # -------------------------------------------------------------- last calls
    dict(
        tag="rtb-quiet",
        mood="routine",
        lines=[
            ("SHEPHERD", "Magic, Shepherd is off station, returning to base.", 0),
            ("MAGIC", "Shepherd, radar contact lost, squawk standby. Good night.", 1.6),
            ("SHEPHERD", "Good night.", 1.2),
        ],
    ),
    dict(
        tag="shift-change",
        mood="routine",
        lines=[
            ("MAGIC", "Sentry, Magic. We're handing over the picture. You've got twelve friendly tracks and one unknown east of Ignus.", 0),
            ("SENTRY", "Sentry copies twelve and one unknown. We have the picture.", 2.2),
            ("MAGIC", "It's been quiet. Try to keep it that way.", 1.6),
            ("SENTRY", "No promises.", 1.4),
        ],
    ),
]
