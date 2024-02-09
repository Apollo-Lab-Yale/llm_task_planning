(define (problem template)
  (:domain virtual-home)
  (:objects
    		kitchen - Room 
		apple_cc12296a - Object
		bowl_89eb4a35 - Object
		bread_ccd7e024 - Object
		butterknife_da1ab1a9 - Object
		cabinet_9625419c - Object
		cabinet_7dfe352a - Object
		cabinet_bac5e58c - Object
		cabinet_375f82d4 - Object
		cabinet_26bffb74 - Object
		cabinet_8256c8ad - Object
		cabinet_163bf462 - Object
		cabinet_c0b733f7 - Object
		cabinet_a7ed67ee - Object
		cabinet_aede3362 - Object
		cabinet_a6dd1224 - Object
		cabinet_f59696cb - Object
		cabinet_d7dba64f - Object
		coffeemachine_0f751c5c - Object
		countertop_1bee114e - Object
		cup_57f70061 - Object
		dishsponge_79e0be84 - Object
		drawer_ffdc818b - Object
		drawer_f8e34777 - Object
		drawer_e7f0bc98 - Object
		drawer_57db6caa - Object
		drawer_3188120f - Object
		egg_fb3557b0 - Object
		faucet_58622ea9 - Object
		floor_64aeea15 - Object
		fork_db82d28b - Object
		fridge_6f1a3578 - Object
		garbagecan_2dfa62fd - Object
		knife_ab70026e - Object
		ladle_08fdd807 - Object
		lettuce_6f4694ec - Object
		lightswitch_4cf4fa46 - Object
		microwave_ef99a644 - Object
		mug_ee360431 - Object
		pan_a4c69ed4 - Object
		peppershaker_ffe7dcf5 - Object
		plate_8004b6ad - Object
		pot_777222e3 - Object
		potato_ab5bf1d7 - Object
		saltshaker_d5ca407a - Object
		sink_5aa7166b - Object
		sinkbasin_031daebd - Object
		soapbottle_9e3525d0 - Object
		spatula_ff13ec0c - Object
		spoon_fbbf0708 - Object
		stool_36eae274 - Object
		stoveburner_5a584b04 - Object
		stoveburner_101357ce - Object
		stoveburner_f82abc65 - Object
		stoveburner_432a2f3f - Object
		stoveknob_1ade2716 - Object
		stoveknob_c912ee58 - Object
		stoveknob_c323bffa - Object
		stoveknob_d3968d55 - Object
		toaster_8e10a86d - Object
		tomato_b6184de1 - Object
		window_25bdf5de - Object

        Apple_cc12296a - Object

        Fridge_6f1a3578 - Object

        kitchen - Room


    character_1 - Character
  )
  (:init
    		(SURFACES cabinet_aede3362)
		(CAN_OPEN cabinet_aede3362)
		(close cabinet_aede3362 character_1)
		(SURFACES cabinet_f59696cb)
		(CAN_OPEN cabinet_f59696cb)
		(close cabinet_f59696cb character_1)
		(SURFACES cabinet_d7dba64f)
		(CAN_OPEN cabinet_d7dba64f)
		(close cabinet_d7dba64f character_1)
		(SURFACES countertop_1bee114e)
		(close countertop_1bee114e character_1)
		(SURFACES cup_57f70061)
		(GRABBABLE cup_57f70061)
		(close cup_57f70061 character_1)
		(IN cup_57f70061 countertop_1bee114e)
		(ON cup_57f70061 countertop_1bee114e)
		(SURFACES fridge_6f1a3578)
		(CAN_OPEN fridge_6f1a3578)
		(close fridge_6f1a3578 character_1)
		(IN fridge_6f1a3578 floor_64aeea15)
		(ON fridge_6f1a3578 floor_64aeea15)
		(GRABBABLE knife_ab70026e)
		(close knife_ab70026e character_1)
		(IN knife_ab70026e countertop_1bee114e)
		(ON knife_ab70026e countertop_1bee114e)
		(SURFACES microwave_ef99a644)
		(HAS_SWITCH microwave_ef99a644)
		(CAN_OPEN microwave_ef99a644)
		(MOVEABLE microwave_ef99a644)
		(close microwave_ef99a644 character_1)
		(IN microwave_ef99a644 countertop_1bee114e)
		(ON microwave_ef99a644 countertop_1bee114e)

        (inside Apple_cc12296a kitchen)

        (inside Fridge_6f1a3578 kitchen)

        (closed Fridge_6f1a3578)

        (grabbable Apple_cc12296a)

        (can_open Fridge_6f1a3578)


    (standing character_1)
  )
  (:goal (and
    (inside Apple_cc12296a Fridge_6f1a3578)
  ))
)