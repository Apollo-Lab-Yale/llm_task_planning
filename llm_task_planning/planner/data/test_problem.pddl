(define (problem put-plates-in-cabinet)
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
		bookshelf_249 - Surface
		bookshelf_249 - Container
		rug_253 - Surface
		rug_253 - Object
		tv_264 - Object
		clothespile_286 - Container
		box_287 - Container
		dishbowl_288 - Object
		book_290 - Object
		book_291 - Object
		book_292 - Object
		book_293 - Object
		condimentbottle_294 - Object
		condimentbottle_295 - Object
		condimentshaker_297 - Object
		box_300 - Container
		photoframe_301 - Object
		paper_302 - Object
		paper_303 - Object
		bananas_316 - Object
		dishbowl_317 - Object
		livingroom_335 - Room
		livingroom_335 - Object
		desk_373 - Surface
		desk_373 - Object
		mouse_429 - Object
		cpuscreen_432 - Object
		computer_433 - Object
		mug_447 - Object


    plate_273 - Object
    plate_277 - Object
    plate_278 - Object
    plate_285 - Object
    kitchencabinet_234 - Container
    kitchentable_231 - Object
    character_1 - Character


  )
  (:init
    		(surfaces bookshelf_249)
		(containers bookshelf_249)
		(surfaces rug_253)
		(grabbable rug_253)
		(sittable rug_253)
		(lieable rug_253)
		(movable rug_253)
		(off tv_264)
		(has_switch tv_264)
		(lookable tv_264)
		(has_plug tv_264)
		(closed clothespile_286)
		(grabbable clothespile_286)
		(can_open clothespile_286)
		(containers clothespile_286)


    (inside plate_273 bathroom_11)
    (inside plate_277 bathroom_11)
    (inside plate_278 bathroom_11)
    (inside plate_285 bathroom_11)
    (inside kitchentable_231 bathroom_11)

    (inside kitchencabinet_234 kitchen_205)
    (closed kitchencabinet_234)
    (can_open kitchencabinet_234)
    (grabbable plate_273)
    (grabbable plate_277)
    (grabbable plate_278)
    (grabbable plate_285)
    (standing character_1)
  )
  (:goal (and
    (inside plate_285 kitchencabinet_234)
    (inside plate_278 kitchencabinet_234)
    (inside plate_277 kitchencabinet_234)
    (inside plate_273 kitchencabinet_234)

  ))
)