(define (problem template)
  (:domain virtual-home)
  (:objects
    		kitchen - Room 
		apple_7414608c - Object
		bowl_21eb5c01 - Object
		bread_0166c008 - Object
		butterknife_81a4be1a - Object
		cabinet_821ae87b - Object
		cabinet_902da35b - Object
		cabinet_94c69f3b - Object
		cabinet_4c1ca2f0 - Object
		cabinet_04115198 - Object
		cabinet_e17cd3fb - Object
		cabinet_bea9d323 - Object
		cabinet_b51bae97 - Object
		cabinet_78fa2972 - Object
		cabinet_e75e613f - Object
		cabinet_f74eee7f - Object
		cabinet_89a2263b - Object
		cabinet_3b0100e2 - Object
		cabinet_192bf5a9 - Object
		cabinet_bc8561c7 - Object
		cabinet_280406e8 - Object
		cabinet_7cf77926 - Object
		cabinet_8591c64a - Object
		cabinet_3adcb9d3 - Object
		cabinet_410b47b9 - Object
		cabinet_b0c0828f - Object
		cabinet_45b6edef - Object
		cabinet_df86d758 - Object
		coffeemachine_e03c53d9 - Object
		countertop_d173ada8 - Object
		countertop_4af54ea8 - Object
		countertop_0ae85ce2 - Object
		cup_743cf4af - Object
		diningtable_226c7fe3 - Object
		dishsponge_fcd908e6 - Object
		drawer_58501a5e - Object
		drawer_4a91ad3a - Object
		drawer_e5ce7d28 - Object
		drawer_8f244ac2 - Object
		egg_bfeeb8dc - Object
		faucet_0942f7ec - Object
		faucet_d8be2e34 - Object
		floor_3bfb2651 - Object
		fork_8fb119be - Object
		fridge_ab2776a0 - Object
		garbagecan_6595174d - Object
		knife_5d27abd6 - Object
		lettuce_470604f9 - Object
		lightswitch_3875b6f6 - Object
		microwave_e7431412 - Object
		mug_c5f962e2 - Object
		pan_2303bbba - Object
		papertowelroll_cf3354f3 - Object
		peppershaker_f3cc2a1a - Object
		plate_37e2b869 - Object
		pot_e063a8ec - Object
		potato_7bde9a7c - Object
		saltshaker_1ebd593a - Object
		sink_2a544275 - Object
		sinkbasin_c1938734 - Object
		soapbottle_db8c0960 - Object
		spatula_fc68984c - Object
		spoon_854f7b5c - Object
		stool_ce737055 - Object
		stoveburner_869804c7 - Object
		stoveburner_e7ac0143 - Object
		stoveburner_e1901038 - Object
		stoveburner_aa9bfe8f - Object
		stoveknob_73cb83c2 - Object
		stoveknob_77a0c15d - Object
		stoveknob_31553689 - Object
		stoveknob_fb6672e1 - Object
		toaster_97eb9cbe - Object
		tomato_ef8f6e91 - Object
		window_2da365b2 - Object

        Apple_7414608c - Object

        Fridge_ab2776a0 - Object

        kitchen - Room


    character_1 - Character
  )
  (:init
    		(SURFACES bowl_21eb5c01)
		(GRABBABLE bowl_21eb5c01)
		(IN bowl_21eb5c01 countertop_0ae85ce2)
		(ON bowl_21eb5c01 countertop_0ae85ce2)
		(GRABBABLE butterknife_81a4be1a)
		(IN butterknife_81a4be1a countertop_0ae85ce2)
		(ON butterknife_81a4be1a countertop_0ae85ce2)
		(SURFACES cabinet_821ae87b)
		(CAN_OPEN cabinet_821ae87b)
		(SURFACES cabinet_902da35b)
		(CAN_OPEN cabinet_902da35b)
		(SURFACES cabinet_94c69f3b)
		(CAN_OPEN cabinet_94c69f3b)
		(SURFACES cabinet_4c1ca2f0)
		(CAN_OPEN cabinet_4c1ca2f0)
		(close cabinet_4c1ca2f0 character_1)
		(SURFACES cabinet_04115198)
		(CAN_OPEN cabinet_04115198)
		(SURFACES cabinet_e17cd3fb)
		(CAN_OPEN cabinet_e17cd3fb)
		(SURFACES cabinet_bea9d323)
		(CAN_OPEN cabinet_bea9d323)
		(SURFACES cabinet_78fa2972)
		(CAN_OPEN cabinet_78fa2972)
		(SURFACES cabinet_e75e613f)
		(CAN_OPEN cabinet_e75e613f)
		(SURFACES cabinet_f74eee7f)
		(CAN_OPEN cabinet_f74eee7f)
		(SURFACES cabinet_89a2263b)
		(CAN_OPEN cabinet_89a2263b)
		(SURFACES cabinet_3b0100e2)
		(CAN_OPEN cabinet_3b0100e2)
		(SURFACES cabinet_192bf5a9)
		(CAN_OPEN cabinet_192bf5a9)
		(SURFACES cabinet_bc8561c7)
		(CAN_OPEN cabinet_bc8561c7)
		(SURFACES cabinet_280406e8)
		(CAN_OPEN cabinet_280406e8)
		(SURFACES cabinet_3adcb9d3)
		(CAN_OPEN cabinet_3adcb9d3)
		(SURFACES cabinet_45b6edef)
		(CAN_OPEN cabinet_45b6edef)
		(SURFACES countertop_0ae85ce2)
		(SURFACES drawer_8f244ac2)
		(CAN_OPEN drawer_8f244ac2)
		(SURFACES floor_3bfb2651)
		(SURFACES fridge_ab2776a0)
		(CAN_OPEN fridge_ab2776a0)
		(IN fridge_ab2776a0 floor_3bfb2651)
		(ON fridge_ab2776a0 floor_3bfb2651)
		(GRABBABLE knife_5d27abd6)
		(IN knife_5d27abd6 countertop_0ae85ce2)
		(ON knife_5d27abd6 countertop_0ae85ce2)
		(SURFACES pan_2303bbba)
		(GRABBABLE pan_2303bbba)
		(IN pan_2303bbba countertop_0ae85ce2)
		(ON pan_2303bbba countertop_0ae85ce2)
		(SURFACES sink_2a544275|SinkBasin)
		(close sink_2a544275|SinkBasin character_1)
		(GRABBABLE soapbottle_db8c0960)
		(IN soapbottle_db8c0960 countertop_0ae85ce2)
		(ON soapbottle_db8c0960 countertop_0ae85ce2)
		(SURFACES toaster_97eb9cbe)
		(HAS_SWITCH toaster_97eb9cbe)
		(MOVEABLE toaster_97eb9cbe)
		(IN toaster_97eb9cbe countertop_0ae85ce2)
		(ON toaster_97eb9cbe countertop_0ae85ce2)

        (inside Apple_7414608c kitchen)

        (inside Fridge_ab2776a0 kitchen)

        (closed Fridge_ab2776a0)

        (grabbable Apple_7414608c)

        (can_open Fridge_ab2776a0)


    (standing character_1)
  )
  (:goal (and
    (inside Apple_7414608c Fridge_ab2776a0)
  ))
)