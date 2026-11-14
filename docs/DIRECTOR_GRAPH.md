# Director Graph Reference (Haydee 1)

Everything here was extracted from the 149 `.edith` maps in `Haydee\Maps\` that
actually contain a director graph (~3,000 node instances) — shipped maps plus a
few custom/EML test maps that live in the same folder — plus behaviour confirmed
by map authors. Counts are instance totals across those maps, so they're a
decent guide to what matters in practice.

> Note: H1 registers **34** director node classes. Haydee 2's editor registers
> **279** (same engine, wider surface). Anything not in the table below is
> either ignored by Edith or refuses to load the map.

---

## 1. Where the graph lives

Inside an `.edith` file (UTF-16LE text), after `content { ... }`:

```
director
{
	x 74;
	y -45;
	nodes
	{
		Enable Enable
		{
			x -305;
			y -172;
			index 2;
			target SpotA;
		}
	}
	links
	{
		link
		{
			input 3 Enable;
			output 1 OnInteract;
		}
	}
}
```

- `x` / `y` on the `director` block = editor canvas scroll position, not gameplay.
- Every node has `x`, `y` (editor position) and an `index` (its ID).
- The line above a node's `{` is `ClassName NodeName`. `NodeName` is only an
  editor label — the runtime identifies nodes by `index`, so renaming a node
  never breaks links.
- `links` is a flat list. Each `link` block pairs an **input** (destination)
  with an **output** (source), both referencing node `index` values.
- Because nodes are referenced by index, **deleting a node shifts nothing but
  leaves dangling links** — always check after editing by hand.

---

## 2. Wiring rules (important, and not what most people assume)

**One output pin can be wired to unlimited input pins.**
**One input pin can accept unlimited links, and fires on any of them.**

Both directions are free wiring. There is no cloning required to branch.

Proof, from `N_Start.edith`:

```
[13] Button source=PurpleButton -> Enable@14.Toggle | Enable@15.Toggle   one button, two actions
[1]  Enable target=PurpleGrate  <- Button@0.OnInteract | Trigger@6.OnTouch | Button@7.OnInteract
```

Older maps in the same folder duplicate the trigger node instead (four
separate `Button source=PurpleButton` nodes each wired to one thing) purely
because the author hadn't realised fan-out worked. Don't copy that habit.

Consequence: when converting graphs or building something big, **branch by
wiring, not by cloning**. A 10-way branch is one node with 10 links, not 10
nodes.

---

## 3. Execution vs value pins

Pins come in two flavours and they are not interchangeable:

- **Execution pins** are capitalised and carry flow: `Input`, `Enable`,
  `Disable`, `Toggle`, `Repeat`, `Output`, `True`, `False`, `OnInteract`,
  `OnTouch`, `OnUnlocked`, `OnEnter`, `OnStartup`, `OnKilled`, `A`, `B`.
- **Value props** are plain fields on the node (`source`, `target`, `sound`,
  `scene`, `entry`, `value`, `state`, `alias`, `class`, `count`, `consume`,
  `minDelay`, `maxDelay`, `minInterval`, `maxInterval`, `steps`, `restart`,
  `default`, `console`). They take text, numbers, or `true`/`false`.

Action nodes generally have one **continuation** output (`Repeat`, or `Output`
on `Once`/`Delay`) so you can chain "do this, then that".

---

## 4. Referring to actors

`source` / `target` take an actor name, and optionally a component:

```
target Door;              whole actor (every component)
target O1_1.Transform;    one component only
source Ambush.Trigger;    one component only
```

Component-qualified names are how you address `Transform` (moving objects),
`Sound`, `Trigger`, `Target`, etc. Enabling/disabling with a bare actor name
hits every component; with `.Component` it hits just that one.

---

## 5. Class reference

Only these 34 exist. `in` = execution/value inputs, `out` = outputs.

| class | props | in | out | does |
|---|---|---|---|---|
| `Enable` (596) | `target` | `Enable` `Disable` `Toggle` | `Repeat` | enable/disable/toggle an actor |
| `Button` (236) | `source` | — | `OnInteract` `OnManual` | player clicks the named button actor |
| `WriteBool` (121) | `target` | `True` `False` `Toggle` | `Repeat` | store a global bool |
| `ReadBool` (88) | `source` `default` | `Input` | `True` `False` | read a global bool |
| `Respawn` (84) | `target` | `Respawn` | `Repeat` | respawn the named **bot** |
| `Once` (77) | — | `Input` | `Output` | passes flow once, then never again |
| `Enabled` (73) | `source` | `Input` | `True` `False` | *is* this actor currently enabled (gate) |
| `GameFX` (56) | `sound` | `Input` | `Repeat` | play a `.sound` cue |
| `Trigger` (51) | `source` | — | `OnTouch` `OnUntouch` `OnToggle` | named trigger volume touched |
| `Locker` (46) | `source` | — | `OnUnlocked` `OnLocked` `OnToggle` | keycard reader / power node socket |
| `Play` (46) | `target` | `Play` | `Repeat` | play an animation **or** drive a `Target` component |
| `Delay` (43) | `minDelay` `maxDelay` | `Input` | `Output` | wait a random time in range, then continue |
| `Entry` (39) | `source` | — | `OnEnter` | player arrived via `Travel` at this entry |
| `WriteInt` (28) | `target` `value` | `Write` | `Repeat` | set a global int to a literal |
| `Item` (25) | `source` | `OnPick` | `OnPick` | named item picked up |
| `Startup` (24) | — | — | `OnStartup` | map finished loading |
| `BotState` (23) | `target` `state` | `Input` | `Repeat` | force bot state (0–3 slasher, 0–2 walker) |
| `ReadInt` (22) | `source` `value` | `Input` | `True` `False` | *is* global int equal to `value` |
| `Lock` (20) | `target` | `Toggle` `Unlock` | `Repeat` | freeze/unfreeze a moving `Transform` |
| `Locked` (12) | `source` | `Input` | `True` `False` | *is* that `Transform` frozen |
| `Travel` (11) | `scene` `entry` `sound` | `Input` | — | send the player to another scene/entry |
| `Achieve` (8) | `alias` | `Achieve` | `Repeat` | unlock a Steam achievement (`HDFree`, `HDCollect`, …) |
| `Custom` (7) | `alias` | `Custom` | `Repeat` | fire a named custom game event |
| `Pawn` (7) | `source` | — | `OnKilled` | the named pawn died |
| `Delete` (7) | `target` | `Delete` | — | destroy an actor |
| `Finish` (5) | `console` | `Finish` | — | end the game / roll ending |
| `Alive` (5) | `source` | `Input` | `True` `False` | *is* the named pawn still alive |
| `HasItem` (4) | `class` `count` `consume` | `Input` | `True` `False` | inventory check |
| `Active` (4) | `source` | `Input` | `True` `False` | *is* the named trigger currently active |
| `Random2` (3) | — | `Input` | `A` `B` | coin flip |
| `Bot` (3) | `source` | — | `OnTarget` | bot noticed the player |
| `Timer` (2) | `minInterval` `maxInterval` `restart` `steps` | `Start` `Stop` | `Elapse` `Step` | repeating timer; `Step` fires once per step |
| `AddInt` (1) | `target` `value` | `Add` | `Repeat` | add to a global int |

The class names above are *both* the class and the usual node name, but the
node name is free text — `Enable Enable` is just convention.

---

## 6. Global storage

`WriteBool` / `ReadBool` / `WriteInt` / `ReadInt` / `AddInt` share one global
namespace, and **it persists across maps and across save/load**.

- Names are arbitrary strings (`ThirdBool`, `BWord`, `DLiftLevel`, `OpenDaDoor`).
- A flag only exists once something writes it. A `ReadBool`/`ReadInt` pointed at
  a name no map has ever written produces **no output at all** — neither `True`
  nor `False` fires, and nothing is logged. The graph does not invent a value.
- This is the only way to carry state between scenes, so it's what every
  multi-part puzzle and every "you already did this" shortcut uses.

### The state-restore idiom

`WAT_Canal.edith` does this and it's the cleanest version of the pattern: on
load, re-apply every persistent flag so the map comes back the way the player
left it.

```
Startup -> ReadBool(source=ThirdBool)  -> Enable(target=CSGThird).Enable
                                      -> Enable(target=ClimbThird).Enable   (chained via Repeat)
```

Two polarities, both useful:

- **default-blocked** — `Startup -> ReadBool -> Enable(True)`. If the flag was
  never set, nothing fires, so the blocker stays.
- **default-present** — `Startup -> Enable.Enable` straight away, then
  `ReadBool -> Enable.Disable` on the true branch. Object exists by default,
  and gets removed if the player already opened it.

`WriteBool` also has a `Toggle` input pin, so a button can flip a flag without
caring about its current value.

### Missing flags don't error — they just aren't there yet

Edith never complains about a flag nobody wrote. A `ReadBool` on `FifthBool`
before any map has set `FifthBool` fires nothing: no `True`, no `False`, no
console noise, no broken graph. It sits inert until the flag exists, then starts
working with no edits.

That's deliberate, and it's why a big hub map can be wired against progression
that isn't finished yet — write the readers now, land the writers later, and the
links stay quiet in between. A "dead" read is not a bug; it's a read waiting for
its writer.

`Toggle` is a one-shot too. It flips the actor's state at the moment it fires
and that's the entire job — the graph doesn't store it, replay it, or re-apply
it on the next load. `Startup -> Enable.Toggle` toggles once when the map opens
and then stops; it does not stack up across sessions.

### Multi-stage doors

```
Button1 -> AddInt(target=OpenDaDoor, value=1)
Button2 -> AddInt(target=OpenDaDoor, value=1)
Button3 -> AddInt(target=OpenDaDoor, value=1)
ReadInt(source=OpenDaDoor, value=3) -> Enable(Door).Disable
```

`WriteInt` sets a literal, `AddInt` increments, `ReadInt` compares.

---

## 7. Sound

Two completely different ways, and the node way is usually the wrong one:

**`GameFX` node** — `sound` prop, `Input` in, `Repeat` out. Works, but you need
one node per event, and it does nothing on its own.

**`EnableSound` component on the actor** — put it on the actor and set its
`source` to the actor's own name. It then plays whenever that actor is enabled
or disabled, with no director nodes at all.

> The `source` field **must be an actor name**. Anything else and it silently
> never plays.

Older maps (e.g. `N_CentralHub`) are full of duplicated `Button` nodes whose
only job is to fire a `GameFX(Door.sound)` next to the `Enable` doing the real
work — that whole second copy is unnecessary with `EnableSound`.

`Play` can also target `Actor.Sound` and play audio, and `Travel` carries its
own `sound` prop, so a scene transition can be scored without a `GameFX`.

---

## 8. Moving things (the `Transform` system)

Moving parts are not animated by the director graph directly:

| node | role |
|---|---|
| `Play` | play a `Target` component's animation (`Water.TargetHigh`, `DoorA.Sound`, …) |
| `Lock` | freeze a `Transform` (`target O1_1.Transform`) — used for "climbable / standable" states |
| `Locked` | *is* that `Transform` frozen (gate) |

`G_RedCross` chains eight of them (`Lock -> Delay -> Lock -> Delay -> …`) to
sequence a platform puzzle. Note `Lock`/`Locked` are **physical state about
geometry**, not keys or keycards. For key locks use `Locker`.

`Delay` (`minDelay`/`maxDelay`, random within range) is the usual way to space
those steps out.

---

## 9. Locks, keys and readers

`Locker` is the keycard reader / power-node socket node. `source` = the reader
actor; `OnUnlocked` fires when a valid card is inserted. `OnLocked` and
`OnToggle` exist but are rarely used.

`HasItem` checks the inventory by **item class**:

```
HasItem(class=Colt, count=1, consume=false) -> True / False
```

`Y_Frame` uses this to detect whether the player is carrying any weapon.

---

## 10. Travel

Two ways to change scene:

- **`Travel` component on a door actor** — normal doors, no graph involvement.
- **`Travel` node** — `scene` + `entry` + `sound` props, triggered by an
  `Input`. Use it when there is no physical door (an elevator call button, a
  scripted transition).

Either way the destination scene fires `Entry(source=E_Something).OnEnter`, so
an arrival trigger is `Entry`, not `Startup`.

`Entry` = "spawn the player at this marker and tell the graph".

---

## 11. Bots

| node | role |
|---|---|
| `Respawn` | respawn a bot actor at its spawn point (`target`, in `Respawn`, out `Repeat`) |
| `BotState` | force a bot's state — 0–3 slashers, 0–2 walkers |
| `Bot` | fires when a bot notices the player (`OnTarget` in shipped maps) |
| `Pawn` | fires when a pawn dies (`OnKilled`) |
| `Alive` | gate: is the pawn still alive |

`Respawn` targets must be **bots**; giving it a non-bot actor does nothing.
Every use in shipped maps targets a `Slasher*` / `Walker*` / `Ambush*` /
`TrapSlasher` / `ObstacleBot`.

---

## 12. Naming rules

Edith is strict about actor names and gives almost no error feedback:

- **No hyphen anywhere** in a name you reference from the director graph.
  `Grate-2` breaks; rename to `Grate2`.
- **The first character must be a letter.** Special characters as the first
  character can make Edith refuse the file.
- Keep names to `[A-Za-z][A-Za-z0-9_]*` and you never hit either rule.
- A node class that Edith doesn't recognise is either silently ignored or it
  refuses the whole map — treat unknown classes as fatal when hand-editing.

---

## 13. Debug notes

- `Trigger` sources often appear as `Actor.Trigger` because the component
  matters; a bare name only works if the actor has exactly one trigger.
- `Startup` fires once per load, after the map is ready — safe place for
  restore logic.
- Node `index` values are IDs, not ordering. They can have gaps and don't need
  to be sequential.
- If a graph "does nothing", check the node's `source`/`target` string against
  the actual actor name character for character. That's the cause ~90% of the time.
- A read wired to a flag **nothing writes yet** is quiet by design, not broken.
  Leave it alone — it wakes up on its own the first time a map writes that flag.
- Edith's default reaction to something it can't resolve is to *skip it*, not to
  throw. Silent no-ops are normal. The only things that actually break a map are
  bad encoding (UTF-8 instead of UTF-16LE), hyphens in referenced names, and
  unknown node classes.

---

## 14. Haydee 2 comparison

Haydee 2 uses the same graph engine ("Graphite") but registers 279 classes
instead of 34, adds object-pointer wiring (`pLocate`, `pGame`, `pPlayer`)
where H1 types a name into a field, and adds control-flow nodes (`Branch`,
`Collect`, `Block`) that H1 handles by plain fan-in/fan-out wiring.

H2 logic maps back to H1 roughly like this:

| H2 | H1 |
|---|---|
| `pLocate` | the actor name in `source` / `target` |
| `bProperty` / `bWrite` / `bToggle` | `ReadBool` / `WriteBool` / `WriteBool.Toggle` |
| `iProperty` / `iWrite` | `ReadInt` / `WriteInt` |
| `OnInteract` / `OnScene` / `OnEntry` / `OnTouch` | `Button` / `Startup` / `Entry` / `Trigger` |
| `OnLock` | `Locker` + a `ReadBool` on the same flag |
| `Collect` | nothing — just wire several sources into one input pin |
| `Branch` | `ReadBool` `True`/`False` |
| `SoundFX` / `rSound` | `EnableSound` component (preferred) or `GameFX` |
| `Spawn` | `Respawn` (re-uses a placed bot, does not create actors) |
| `pGame` / `Note` / `Block` | drop |

---

# Part II — Recipes

Copy-paste wiring for the things people actually build. `A -> B.pin` means
link A's continuation output (`Repeat` / `Output` / trigger pin) into B's
`pin` input. Prose above explains *why*; this is *how*.

### 1. Simple button door

```
Button(source=DoorButton)
  -> Enable(target=Door).Toggle
```

`Toggle` flips state, so pressing again closes it. If you want open-only, use
`.Disable` on a door that starts enabled, or `.Enable` on one that starts
disabled.

### 2. Button door with sound, no GameFX

Attach an `EnableSound` component to `Door`, set its `source` to `Door`, point
it at a `.sound` file. Wiring stays as recipe 1 — the sound fires because the
actor was enabled/disabled. **One node, no duplication.**

### 3. Keycard reader

```
Locker(source=CardReader)
  -> Enable(target=SecDoor).Disable      (or .Toggle)
  -> GameFX(sound="Sounds\Common\Door.sound").Input   (only if you have no EnableSound)
```

`Locker.source` is the **reader** actor, not the door. `OnUnlocked` fires on a
valid card. `OnLocked` / `OnToggle` exist but are rarely used in shipped maps.

### 4. Door that needs three buttons (persistent)

```
Button(source=B1) -> AddInt(target=HubDoors, value=1)
Button(source=B2) -> AddInt(target=HubDoors, value=1)
Button(source=B3) -> AddInt(target=HubDoors, value=1)
ReadInt(source=HubDoors, value=3)
  -> True  -> Enable(target=HubDoor).Disable
  -> True  -> Achieve(alias=HDCollect).Achieve       (optional)
```

Because `OpenDaDoor`/`BWord`-style ints persist, re-entering the map keeps the
door open. Don't use three `Once` nodes for this — they reset on reload.

### 5. Shortcut that stays open forever

Write the flag where the shortcut is first opened, then restore it on load:

```
(where the shortcut opens)
Enable(target=Wall).Disable -> WriteBool(target=ShortcutA).True

(on load)
Startup -> ReadBool(source=ShortcutA, default=false)
           -> True -> Enable(target=Wall).Disable
```

See §6 for the two restore polarities.

### 6. Restore many flags at once

`Startup` outputs to as many `ReadBool` nodes as you want — no cloning:

```
Startup -> ReadBool(source=ShortcutA) -> Enable(target=WallA).Disable
        -> ReadBool(source=ShortcutB) -> Enable(target=WallB).Disable
        -> ReadBool(source=ShortcutC) -> Enable(target=WallC).Disable
```

Chain with `Repeat` if you need them in a specific order; separate links if
order doesn't matter.

### 7. Light switch (toggle + memory)

```
Button(source=LightSwitch)
  -> WriteBool(target=LightOn).Toggle
  -> Enable(target=LightCage).Toggle
```

Both fire on the same press because fan-out is free. Restore on load with
`ReadBool(source=LightOn)`.

### 8. One-time event that must not repeat

```
Trigger(source=AmbushTrap)
  -> Once -> Enable(target=TrapDoor).Disable
         -> Respawn(target=SlasherA).Respawn
         -> Respawn(target=SlasherB).Respawn
```

`Once` survives nothing on reload — it only stops re-fires within a session.
For cross-session one-time, use a `WriteBool` + `ReadBool` guard instead.

### 9. Timed trap

```
Button(source=TrapButton)
  -> Delay(minDelay=1.5, maxDelay=1.5)
    -> Enable(target=Crusher).Enable
    -> Delay(minDelay=3.0, maxDelay=3.0)
      -> Enable(target=Crusher).Disable
```

`minDelay`/`maxDelay` is a **range**; equal values mean a fixed delay. Random
timing is just unequal values.

### 10. Repeating timer with N steps

```
Button(source=StartMachine) -> Timer(minInterval=2.5, maxInterval=2.5, steps=10, restart=false).Start
Timer.Step   -> Enable(target=Blinker).Toggle      (fires once per step)
Timer.Elapse -> Enable(target=MachineFinal).Disable
```

`Step` is the per-tick output; `Elapse` fires when the run completes.
`restart=true` loops forever.

### 11. Ambush wave

```
Trigger(source=AmbushZone)
  -> Respawn(target=AmbushA).Respawn
  -> Respawn(target=AmbushB).Respawn
  -> Respawn(target=AmbushC).Respawn
  -> GameFX(sound="Sounds\Common\Ambush.sound").Input
```

One `Respawn` per bot — `target` holds a single actor name, so this is the one
case where you legitimately need N nodes (not cloned triggers, N different
targets).

### 12. Elevator with no door actor

```
Locker(source=ElevatorCall) -> Travel(scene=Level2, entry=E_Level2, sound="Sounds\Common\Block.sound").Input
```

Use the `Travel` **node** only when there's no `Travel` component to trigger.
Door actors should use the component and stay out of the graph entirely.

### 13. Moving platform

```
Button(source=PlatformButton) -> Play(target=Lift.TargetHigh).Play
Locked(source=Lift.Transform) -> True -> Enable(target=TopDoor).Enable
```

`Play` drives a `Target` component's saved position. `Locked`/`Lock` handle
the "is it currently locked/frozen" state for standable surfaces.

### 14. Sequenced platform puzzle

```
Play -> Lock(target=O1_1.Transform).Toggle
     -> Delay(0.5, 0.5) -> Lock(target=O1_2.Transform).Toggle
     -> Delay(0.5, 0.5) -> Lock(target=O1_3.Transform).Toggle
     -> Locked(source=O1_3.Transform) -> True -> Enable(target=Exit).Enable
```

That's the `G_RedCross` shape: chain `Lock`/`Locked` per `Transform`, space
with `Delay`, gate the exit on the last one.

### 15. Branch on a condition

```
ReadBool(source=HasKey) -> True  -> Enable(target=SecretDoor).Disable
                        -> False -> GameFX(sound="Sounds\Common\Beep.sound").Input
```

`ReadBool`, `ReadInt`, `Enabled`, `Alive`, `Locked`, `Active`, `HasItem` all
share the same `True`/`False` gate shape — swap them freely.

### 16. Inventory gate

```
HasItem(class=Colt, count=1, consume=false) -> True -> Enable(target=Armory).Enable
```

Note `class` is the **item class**, not an actor name. `consume=true` spends
the item when the check passes.

### 17. Player death hook

```
Pawn(source=Haydee) -> OnKilled -> Delete(target=Alarm).Delete
```

`Pawn.source` is the pawn actor's name. Same node handles boss pawns
(`Pawn(source=Master)`) for phase transitions.

### 18. Ending

```
Trigger(source=ExitZone)
  -> Finish(console=Free).Finish
  -> Achieve(alias=HDFree).Achieve
  -> Custom(alias=EndGame).Custom
```

`Finish.console` is the ending identifier (`Free`, `Master`, `Paradox`,
`Trapped`) — confusingly named, but that's the field. `Achieve.alias` is the
Steam achievement id. `Custom.alias` fires a named game event.

### 19. Random branch

```
Trigger(source=MysteryBox) -> Random2 -> A -> Enable(target=RewardA).Enable
                                      -> B -> Enable(target=RewardB).Enable
```

### 20. Bot becomes aggressive on alert

```
Bot(source=SlasherA) -> OnTarget -> BotState(target=SlasherA, state=2).Input
```

`state` is an int: 0–3 slashers, 0–2 walkers. `Bot` only exposes `OnTarget` in
shipped maps.

### 21. Convergence hub — one map, every flag

The pattern that makes a multi-map campaign feel continuous: the hub map reads
every flag the other maps can write, all from a single `Startup`.

```
Startup -> ReadBool(source=FlagA) -> Enable(target=IslandA).Enable
                                 -> Enable(target=ClimbA).Enable
        -> ReadBool(source=FlagB) -> Enable(target=IslandB).Enable
        -> ReadBool(source=FlagC) -> Enable(target=IslandC).Enable
        -> ReadBool(source=FlagD) -> Enable(target=IslandD).Enable
```

One `Startup` fans out to four `ReadBool` nodes, and each `ReadBool` fans out to
its geometry. No cloning, no ordering requirement. Flags nobody has written yet
just stay silent, so the hub is safe to build before the rest of the campaign
exists.

### 22. Arrival stamp — "which way did the player come in?"

A small map that only exists to record direction of travel. Two lifts to the
same hub each stamp their own flag on load, and the hub branches on it:

```
(ToBoiler)  Startup -> WriteBool(target=CameFromBoiler).True
(ToGate)    Startup -> WriteBool(target=CameFromGate).True

(hub)       Startup -> ReadBool(source=CameFromBoiler) -> True -> Enable(target=BoilerDoor).Disable
```

Useful when the same entry point should behave differently depending on where
the player came from, and the level has no distinct entry markers to key off.

### 23. Cascade restore — chains of shortcuts

When shortcut N+1 supersedes shortcut N, restoring them is a cascade: enabling
one disables the one before it, so the player always ends up on the newest
route instead of all of them stacked.

```
Startup -> ReadBool(source=FourthBool) -> Enable(target=Shortcut4).Enable
                                       -> Enable(target=Old4).Disable
        -> ReadBool(source=FifthBool)  -> Enable(target=Shortcut5).Enable
                                       -> Enable(target=Shortcut4).Disable
        -> ReadBool(source=SixthBool)  -> Enable(target=Shortcut6).Enable
                                       -> Enable(target=Shortcut5).Disable
```

Every branch is independent, so the order they fire in doesn't matter — the
highest flag that exists wins. If your shortcut list ever grows, append a branch
and update only the "disable the previous one" target.

### 24. Component-scoped trigger

```
Trigger(source=Trig.TriggerAmb) -> Enable(target=Ambush).Enable
```

`Actor.Component` in `source` fires on that one component only. Use it when the
actor carries several triggers and you don't want all of them, or when the same
actor also does something else.

---

# Part III — Reference tables

## 15. Pin reverse lookup

Pin → where it appears. Useful when you're staring at a link and don't know
what feeds it.

| pin | class | meaning |
|---|---|---|
| `Input` | ReadBool, ReadInt, Enabled, Alive, Locked, HasItem, Active, GameFX, Delay, BotState, Once, Random2, SceneFX, Travel | "run this node now" |
| `Enable` | Enable | force enabled |
| `Disable` | Enable | force disabled |
| `Toggle` | Enable, WriteBool, Lock | flip current state |
| `Repeat` | Enable, WriteBool, WriteInt, AddInt, Play, GameFX, BotState, Achieve, Custom, Lock, Respawn | continue chain after acting |
| `Output` | Once, Delay | continue chain |
| `True` / `False` | ReadBool, ReadInt, Enabled, Alive, Locked, HasItem, Active | gate result |
| `OnInteract` | Button | player clicked |
| `OnManual` | Button | manually fired (rare) |
| `OnTouch` / `OnUntouch` / `OnToggle` | Trigger | volume entered / left / toggled |
| `OnUnlocked` / `OnLocked` / `OnToggle` | Locker | card accepted / rejected / toggled |
| `OnEnter` | Entry | player arrived at entry |
| `OnStartup` | Startup | map loaded |
| `OnKilled` | Pawn | pawn died |
| `OnTarget` | Bot | bot acquired player |
| `OnPick` | Item | item picked up (also an input pin of the same name) |
| `Write` | WriteInt | commit the value |
| `Add` | AddInt | increment |
| `Play` | Play | run the animation |
| `Respawn` | Respawn | respawn the bot |
| `Delete` | Delete | destroy actor |
| `Finish` | Finish | end game |
| `Achieve` | Achieve | unlock |
| `Custom` | Custom | fire event |
| `Start` / `Stop` | Timer | start / stop timer |
| `Step` / `Elapse` | Timer | every tick / on completion |
| `Unlock` | Lock | unfreeze a transform |
| `A` / `B` | Random2 | coin flip results |

## 16. Prop value types

| prop | type | used by | notes |
|---|---|---|---|
| `source` | actor name | Button, ReadBool, ReadInt, Enabled, Locked, Trigger, Locker, Entry, Item, Pawn, Bot, Active, Alive | accepts `Actor` or `Actor.Component` |
| `target` | actor name | Enable, WriteBool, WriteInt, AddInt, Respawn, BotState, Lock, Delete, Play | same syntax |
| `sound` | quoted path | GameFX, Travel, SceneFX | `"Sounds\Common\Door.sound"` |
| `scene` | scene name | Travel | no quotes |
| `entry` | actor name | Travel | entry marker in the destination scene |
| `default` | bool | ReadBool | declared fallback value (`false` in 85 of 88 maps). In practice a flag nothing has written produces **no** output rather than a `false` — see §6 |
| `value` | int | WriteInt, ReadInt, AddInt | `WriteInt` sets it, `ReadInt` compares against it, `AddInt` adds it |
| `state` | int | BotState | 0–3 slasher, 0–2 walker |
| `alias` | string | Achieve, Custom | `HDFree`, `EndGame`, `WordNude`, … |
| `class` | item class | HasItem | `Colt`, `Magnum`, `SMG`, `RemoteControl` |
| `count` | int | HasItem | required amount |
| `consume` | bool | HasItem | spend the item on success |
| `minDelay` / `maxDelay` | float | Delay | seconds, random in range |
| `minInterval` / `maxInterval` | float | Timer | seconds between steps |
| `steps` | int | Timer | number of steps before `Elapse` |
| `restart` | bool | Timer | loop forever |
| `console` | string | Finish | ending id (`Free`, `Master`, `Paradox`, `Trapped`) |
| `x` / `y` | int | every node | editor canvas position |
| `index` | int | every node | node ID used by links |

## 17. Hand-editing a graph safely

Edith is unforgiving here, so run these checks every time:

1. **Every `index` is unique within the map.** Duplicates silently break links.
2. **Every link's two indexes exist.** Deleting a node without removing its
   links leaves dangling entries.
3. **Nodes block comes before links block**, both inside `director { }`.
4. **File is UTF-16LE with BOM.** Saving as UTF-8 makes Edith refuse the map.
5. **No hyphens** and no non-letter first characters in any referenced actor name.
6. **No unknown class names.** Unregistered nodes are ignored or fatal — never
   leave one in "to finish later".
7. **Back up before every save.** See the EML safety tools; `CreateFileA` with
   `CREATE_ALWAYS` truncates the file the instant saving starts, so a crash
   mid-save leaves an empty/corrupt `.edith`.
8. **Test with F5, not by compiling.** Compilation bakes a `.scene` and throws
   away the graph — you can't debug a baked scene.

## 18. Troubleshooting

| symptom | usual cause |
|---|---|
| node does nothing | `source`/`target` string doesn't match an actor name exactly (case-sensitive, no hyphen) — **or** it reads a flag no map has written yet, which is normal |
| read never fires | the flag it reads has never been written. Wire the writer and it starts working; no other change needed |
| `Toggle` fired but state came back later | `Toggle` is a one-shot action, not stored state — nothing re-applies it. Re-apply from `Startup` if you want it every load |
| works in editor, dead in game | node left in uncompiled `.edith` and the `.scene` is stale — recompile |
| fires twice | trigger volume overlaps two actors, or two `Trigger` nodes on the same volume |
| fires once then never again | `Once` upstream, or a `WriteBool` guard already set from a previous session |
| sound silent | `EnableSound.source` isn't an actor name, or `GameFX` input never fires |
| door re-locks after reload | no `Startup` + `ReadBool` restore, so the map's default state wins |
| links "disappeared" | an `index` was duplicated or a node was deleted leaving gaps |
| map refuses to load | unknown node class, bad charset (UTF-8 instead of UTF-16LE), or a hyphenated name |

