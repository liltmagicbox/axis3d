"""vectorized branchless FSM demo.
100k mobs, 4 states: IDLE / CHASE / FLEE / DEAD.
- per-state behavior  = coefficient lookup tables (no branch, no mask-gather)
- transitions         = masked writes / np.select / transition table (3 variants)
- on-enter effects    = nonzero over (state != prev), python touches only the few
"""
import numpy as np
import time

tt = time.perf_counter

IDLE, CHASE, FLEE, DEAD = 0, 1, 2, 3

N = 100_000
rng = np.random.default_rng(0)

state = np.zeros(N, np.int8)                      # small dtype: cache friendly
pos   = (rng.random((N, 2), np.float32)) * 200
vel   = np.zeros((N, 2), np.float32)
hp    = np.full(N, 100.0, np.float32)
timer = np.zeros(N, np.float32)                   # time since last transition
player = np.array([100.0, 100.0], np.float32)

# ---- the heart: per-state parameters as tables, indexed by state ----
SPEED     = np.array([0.0, 3.0, 6.0, 0.0], np.float32)   # idle, chase, flee, dead
MOVE_SIGN = np.array([0.0, -1.0, 1.0, 0.0], np.float32)  # -1: toward player, +1: away
REGEN     = np.array([2.0, 0.0, 1.0, 0.0], np.float32)   # hp per second


def sense():
	"compute everyone's senses in one sweep. logic reads these, never recomputes."
	d = pos - player                          # points away from player
	dist = np.sqrt((d * d).sum(axis=1))
	away = d / (dist[:, None] + 1e-9)         # unit vector, safe at 0
	return dist, away


# ---------------- transitions: 3 equivalent styles ----------------

def transitions_masked(dist):
	"style 1: one masked write per rule. later writes override -> priority by order."
	near     = dist < 60.0
	low_hp   = hp < 45.0
	timeout  = timer > 3.0
	died     = hp <= 0.0
	state[(state == IDLE) & near]    = CHASE
	state[(state == CHASE) & low_hp] = FLEE
	state[(state == FLEE) & timeout] = IDLE
	state[died]                      = DEAD    # applied last = strongest


def transitions_select(dist):
	"style 2: np.select. first matching condition wins -> priority by list order."
	near, low_hp = dist < 60.0, hp < 45.0
	timeout, died = timer > 3.0, hp <= 0.0
	state[:] = np.select(
		[died,
		 (state == CHASE) & low_hp,
		 (state == IDLE) & near,
		 (state == FLEE) & timeout],
		[DEAD, FLEE, CHASE, IDLE],
		default=state)


# style 3: table-driven automaton. the whole FSM is one 2d array.
#   event ids: 0 none, 1 near, 2 low_hp, 3 timeout, 4 died
E_NONE, E_NEAR, E_LOWHP, E_TIMEOUT, E_DIED = 0, 1, 2, 3, 4
TRANS = np.tile(np.arange(4, dtype=np.int8)[:, None], (1, 5))  # default: stay
TRANS[IDLE,  E_NEAR]    = CHASE
TRANS[CHASE, E_LOWHP]   = FLEE
TRANS[FLEE,  E_TIMEOUT] = IDLE
TRANS[:,     E_DIED]    = DEAD

def transitions_table(dist):
	event = np.select(
		[hp <= 0.0, hp < 45.0, dist < 60.0, timer > 3.0],
		[E_DIED, E_LOWHP, E_NEAR, E_TIMEOUT], E_NONE)
	state[:] = TRANS[state, event]


# ---------------- one frame ----------------

def tick(dt, transitions):
	dist, away = sense()

	prev = state.copy()
	transitions(dist)

	# on-enter: python touches only entities that changed state this frame
	changed = np.nonzero(state != prev)[0]
	timer[changed] = 0.0
	# for i in changed: play_sound, spawn_effect ...   (few, so python is fine)

	# per-state behavior, branchless: dead entities get 0 speed / 0 regen
	vel[:] = away * (MOVE_SIGN[state] * SPEED[state])[:, None]
	pos[:] += vel * dt          # note: bare `pos +=` would rebind -> UnboundLocalError
	np.minimum(hp + REGEN[state] * dt, 100.0, out=hp)
	timer[:] += dt
	return changed.size


if __name__ == '__main__':
	# damage pulse so states actually cycle in the demo
	def run(name, transitions, frames=300):
		state[:] = IDLE; hp[:] = 100; timer[:] = 0
		pos[:] = rng.random((N, 2), np.float32) * 200
		best = 1e9; total_changed = 0
		for f in range(frames):
			hp[rng.integers(0, N, 2000)] -= 20.0      # random damage
			t = tt()
			total_changed += tick(1 / 60, transitions)
			d = tt() - t
			if d < best: best = d
		counts = np.bincount(state, minlength=4)
		print(f"{name:8s}: best {best*1000:5.2f} ms/frame   "
			  f"idle {counts[0]:>6} chase {counts[1]:>6} flee {counts[2]:>6} dead {counts[3]:>6}   "
			  f"transitions {total_changed}")

	run('masked', transitions_masked)
	run('select', transitions_select)
	run('table',  transitions_table)
