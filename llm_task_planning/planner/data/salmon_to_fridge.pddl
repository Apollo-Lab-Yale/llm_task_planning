(define (problem put-salmon-in-fridge)
  (:domain virtual-home)
  (:objects
    OBJECT_TEMP

    fridge_305 - Object
    salmon_327 - Object
  )
  (:init
    PRED_TEMP


    (inside salmon_327 $$$)
    (inside fridge_305 kitchen_205)
    (closed fridge_305)
    (grabbable salmon_327)
    (can_open fridge_305)
    (standing character_1)
  )
  (:goal (and
    (inside salmon_327 fridge_305)
  ))
)