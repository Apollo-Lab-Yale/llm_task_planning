(define (problem cook-salmon-in-microwave)
  (:domain virtual-home)
  (:objects
    OBJECT_TEMP

    breadslice_309 - Object
    toaster_308 - Object
  )
  (:init
    PRED_TEMP


    (inside breadslice_309 $$$)
    (inside toaster_308 kitchen_205)
    (grabbable breadslice_309)
    (can_open toaster_308)
    (can_cook toaster_308)
    (has_switch toaster_308)
    (standing character_1)
    (closed toaster_308)
    (off toaster_308)
  )
  (:goal (and
    (cooked breadslice_309 toaster_308)
  ))
)