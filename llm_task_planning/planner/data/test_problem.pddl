(define (problem cook-salmon-in-microwave)
  (:domain virtual-home)
  (:objects
    		character_1 - Character
		character_1 - Object
		bathroom_11 - Room
		bathroom_11 - Object
		bedroom_73 - Room
		bedroom_73 - Object
		kitchen_205 - Room
		kitchen_205 - Object
		kitchencabinet_236 - Surface
		kitchencabinet_236 - Container
		kitchencabinet_237 - Surface
		kitchencabinet_237 - Container
		faucet_248 - Object
		microwave_313 - Container
		bellpepper_320 - Object
		bellpepper_321 - Object
		bellpepper_322 - Object
		bellpepper_323 - Object
		bellpepper_324 - Object
		bellpepper_325 - Object
		dishbowl_326 - Object
		livingroom_335 - Room
		livingroom_335 - Object


    fridge_305 - Object
    salmon_327 - Object
    microwave_313 - Object
  )
  (:init
    		(closed kitchencabinet_236)
		(surfaces kitchencabinet_236)
		(can_open kitchencabinet_236)
		(containers kitchencabinet_236)
		(closed kitchencabinet_237)
		(surfaces kitchencabinet_237)
		(can_open kitchencabinet_237)
		(containers kitchencabinet_237)
		(off faucet_248)
		(has_switch faucet_248)
		(closed microwave_313)
		(active microwave_313)
		(can_open microwave_313)
		(has_switch microwave_313)
		(containers microwave_313)
		(has_plug microwave_313)
		(grabbable bellpepper_320)
		(movable bellpepper_320)
		(grabbable bellpepper_321)
		(movable bellpepper_321)
		(grabbable bellpepper_322)
		(movable bellpepper_322)
		(grabbable bellpepper_323)
		(movable bellpepper_323)
		(grabbable bellpepper_324)
		(movable bellpepper_324)
		(grabbable bellpepper_325)
		(movable bellpepper_325)
		(grabbable dishbowl_326)
		(recipient dishbowl_326)
		(movable dishbowl_326)
		(inside kitchencabinet_236 kitchen_205)
		(inside kitchencabinet_237 kitchen_205)
		(inside faucet_248 kitchen_205)
		(inside microwave_313 kitchen_205)
		(inside bellpepper_320 kitchen_205)
		(inside bellpepper_321 kitchen_205)
		(inside bellpepper_322 kitchen_205)
		(inside bellpepper_323 kitchen_205)
		(inside bellpepper_324 kitchen_205)
		(inside bellpepper_325 kitchen_205)
		(inside dishbowl_326 kitchen_205)
		(holds_rh character_1 salmon_327)
		(close character_1 bellpepper_321)
		(close bellpepper_321 character_1)
		(close character_1 microwave_313)
		(close microwave_313 character_1)
		(close character_1 bellpepper_325)
		(close bellpepper_325 character_1)
		(close character_1 dishbowl_326)
		(close dishbowl_326 character_1)
		(close character_1 bellpepper_320)
		(close bellpepper_320 character_1)
		(close character_1 bellpepper_324)
		(close bellpepper_324 character_1)
		(close character_1 bellpepper_322)
		(close bellpepper_322 character_1)
		(close character_1 bellpepper_323)
		(close bellpepper_323 character_1)
		(close character_1 kitchencabinet_237)
		(close kitchencabinet_237 character_1)
		(close character_1 faucet_248)
		(close faucet_248 character_1)
		(close character_1 kitchencabinet_236)
		(close kitchencabinet_236 character_1)
		(inside character_1 kitchen_205)



    (inside salmon_327 kitchen_205)
    (inside microwave_313 kitchen_205)
    (grabbable salmon_327)
    (can_open microwave_313)
    (can_cook microwave_313)
    (has_switch microwave_313)
    (standing character_1)
    (closed microwave_313)
    (off microwave_313)
  )
  (:goal (and
    (cooked salmon_327 microwave_313)
  ))
)