(define (problem put-plates-in-cabinet)
  (:domain virtual-home)
  (:objects
    OBJECT_TEMP

    plate_273 - Object
    plate_277 - Object
    plate_278 - Object
    plate_285 - Object
    kitchencabinet_234 - Container
    kitchentable_231 - Object
    character_1 - Character


  )
  (:init
    PRED_TEMP
    (inside plate_273 $$$)
    (inside plate_277 $$$)
    (inside plate_278 $$$)
    (inside plate_285 $$$)
    (inside kitchentable_231 $$$)

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
    ;(inside plate_285 kitchencabinet_234)
    (inside plate_278 kitchencabinet_234)
    (inside plate_277 kitchencabinet_234)
    (inside plate_273 kitchencabinet_234)

  ))
)