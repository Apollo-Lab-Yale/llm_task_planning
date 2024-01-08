(define (problem cook-salmon-in-microwave)
  (:domain virtual-home)
  (:objects
    OBJECT_TEMP

    fridge_305 - Object
    salmon_327 - Object
    microwave_313 - Object
    kitchentable_231 - Object
  )
  (:init
    PRED_TEMP

    (inside salmon_327 $$$)
    (inside microwave_313 kitchen_205)
    (grabbable salmon_327)
    (can_open microwave_313)
    (can_cook microwave_313)
    (has_switch microwave_313)
    (standing character_1)
    (closed microwave_313)
    (off microwave_313)
    (inside kitchentable_231 kitchen_205)
  )
  (:goal (and
    (cooked salmon_327 microwave_313)
    ;(on salmon_327 kitchentable_231)
  ))
)