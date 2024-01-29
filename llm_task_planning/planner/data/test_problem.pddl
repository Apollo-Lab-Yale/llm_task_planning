(define (problem template)
  (:domain virtual-home)
  (:objects
    		kitchen - Room 
		apple_32d35e39 - Object
		cabinet_ca132dd5 - Object
		cabinet_32d7d810 - Object
		cabinet_2351cf09 - Object
		cabinet_d301c56d - Object
		cabinet_1145598c - Object
		chair_ced5dcc3 - Object
		coffeemachine_c8efc2e0 - Object
		countertop_5007e1d7 - Object
		diningtable_524ab915 - Object
		drawer_2a7a63de - Object
		floor_e4c4b9c9 - Object
		fridge_bfd34d04 - Object
		knife_7fdb365f - Object
		mug_61ceff58 - Object
		pot_050e5f26 - Object

            Mug_61ceff58 - Object

            SinkBasin_a30cb5f1 - Object

            Faucet_788b50e3 - Object


            kitchen - Room


    character_1 - Character
  )
  (:init
    		(GRABBABLE apple_32d35e39)
		(SURFACES cabinet_ca132dd5)
		(CAN_OPEN cabinet_ca132dd5)
		(SURFACES cabinet_32d7d810)
		(CAN_OPEN cabinet_32d7d810)
		(SURFACES cabinet_2351cf09)
		(CAN_OPEN cabinet_2351cf09)
		(SURFACES cabinet_d301c56d)
		(CAN_OPEN cabinet_d301c56d)
		(SURFACES cabinet_1145598c)
		(CAN_OPEN cabinet_1145598c)
		(SURFACES chair_ced5dcc3)
		(MOVEABLE chair_ced5dcc3)
		(SURFACES coffeemachine_c8efc2e0)
		(HAS_SWITCH coffeemachine_c8efc2e0)
		(MOVEABLE coffeemachine_c8efc2e0)
		(SURFACES countertop_5007e1d7)
		(SURFACES diningtable_524ab915)
		(MOVEABLE diningtable_524ab915)
		(SURFACES drawer_2a7a63de)
		(CAN_OPEN drawer_2a7a63de)
		(SURFACES floor_e4c4b9c9)
		(SURFACES fridge_bfd34d04)
		(CAN_OPEN fridge_bfd34d04)
		(GRABBABLE knife_7fdb365f)
		(SURFACES mug_61ceff58)
		(DIRTY mug_61ceff58)
		(GRABBABLE mug_61ceff58)
		(SURFACES pot_050e5f26)
		(GRABBABLE pot_050e5f26)

            (inside Mug_61ceff58 kitchen)

            (water_source Faucet_788b50e3)

            (cleaning_target SinkBasin_a30cb5f1)

            (has_switch Faucet_788b50e3)

            (grabbable Mug_61ceff58)

            (open SinkBasin_a30cb5f1)

            (off Faucet_788b50e3)


    (standing character_1)
  )
  (:goal (and
    (not (dirty Mug_61ceff58))
  ))
)