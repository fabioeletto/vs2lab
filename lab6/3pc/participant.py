import random
import logging
from const3PC import *
import stablelog

class Participant:
    def __init__(self, chan):
        self.channel = chan
        self.participant = self.channel.join('participant')
        self.stable_log = stablelog.create_log("participant-" + self.participant)
        self.logger = logging.getLogger("vs2lab.lab6.3pc.Participant")
        self.coordinator = {}
        self.all_participants = {}
        self.state = None

    def _enter_state(self, state):
        self.stable_log.info(state)
        self.logger.info("Participant {} entered state {}."
                         .format(self.participant, state))
        self.state = state

    @staticmethod
    def _do_work():
        # if random.random() > 0:
        #     return LOCAL_ABORT
        return LOCAL_SUCCESS

    def init(self):
        self.channel.bind(self.participant)
        self.coordinator = self.channel.subgroup('coordinator')
        self.all_participants = self.channel.subgroup('participant')
        self._enter_state(INIT)

    def _handle_coordinator_failure(self):
        # Become new coordinator or follow another one
        participants = sorted(list(self.all_participants), key=lambda x: int(x))
        new_coordinator = participants[0]  # smallest id becomes coordinator
        
        if self.participant == new_coordinator:
            self.logger.info(f"Participant {self.participant} became new coordinator.")

            # I am the new coordinator
            self.channel.send_to(self.all_participants, STATE_REQUEST)
            states = {self.participant: self.state}
            
            # Collect states from other participants
            for _ in range(len(self.all_participants) - 1):
                msg = self.channel.receive_from(self.all_participants, TIMEOUT)
                if msg and msg[1][0] == STATE_RESPONSE:  # msg[1] ist jetzt ein Tupel
                    states[msg[0]] = msg[1][1]  # zweites Element ist der Zustand
            
            # Determine final state based on collected states
            if COMMIT in states.values():
                decision = GLOBAL_COMMIT
            elif PRECOMMIT in states.values():
                decision = GLOBAL_COMMIT
            else:
                decision = GLOBAL_ABORT
                
            self.channel.send_to(self.all_participants, decision)
            return decision
        else:
            # Wait for new coordinator with timeout
            retry_count = 0
            while retry_count < 3:  # Maximum 3 Versuche
                msg = self.channel.receive_from_any(TIMEOUT)
                if not msg:
                    retry_count += 1
                    continue
                    
                if msg[1] == STATE_REQUEST:
                    self.channel.send_to({msg[0]}, (STATE_RESPONSE, self.state))
                elif msg[1] in [GLOBAL_COMMIT, GLOBAL_ABORT]:
                    return msg[1]
            
            # Nach Timeout: Abbruch
            return GLOBAL_ABORT

    def run(self):
        # if random.random() > 0.5: # crash coordinator wait
        #     return f"Participant {self.participant} crashed in state INIT."

        # Phase 1: Vote
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)
        if not msg:
            self._enter_state(ABORT)
            return f"Participant {self.participant} aborted: coordinator failed before vote request"

        assert msg[1] == VOTE_REQUEST
        decision = self._do_work()

        if decision == LOCAL_ABORT:
            self._enter_state(ABORT)
            self.channel.send_to(self.coordinator, VOTE_ABORT)
            return f"Participant {self.participant} aborted: local work failed"

        self._enter_state(READY)
        self.channel.send_to(self.coordinator, VOTE_COMMIT)

        # if random.random() > 0.5: # crash coordinator precommit
        #     return f"Participant {self.participant} crashed in state READY."
        

        # Phase 2: PreCommit
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)
        if not msg:
            decision = self._handle_coordinator_failure()
        else:
            decision = msg[1]

        if decision == GLOBAL_ABORT:
            self._enter_state(ABORT)
            return f"Participant {self.participant} aborted: received global abort"
        
        assert decision == PREPARE_COMMIT
        self._enter_state(PRECOMMIT)
        self.channel.send_to(self.coordinator, READY_COMMIT)

        # if random.random() > 0.5: # crash coordinator wait
        #     return f"Participant {self.participant} crashed in state PRECOMMIT."

        # Phase 3: Commit
        msg = self.channel.receive_from(self.coordinator, TIMEOUT)
        if not msg:
            decision = self._handle_coordinator_failure()
        else:
            decision = msg[1]

        if decision == GLOBAL_COMMIT:
            self._enter_state(COMMIT)
            return f"Participant {self.participant} committed"
        else:
            self._enter_state(ABORT)
            return f"Participant {self.participant} aborted in final phase" 