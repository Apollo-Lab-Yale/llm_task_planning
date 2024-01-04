(define (domain virtual-home)
(:requirements :strips :typing :equality :disjunctive-preconditions :conditional-effects)
(:types Character
      Object
      Room
      Surface - Object
      Container - Object
)

  (:predicates
    ; States
    (open ?obj - Object)
    (closed ?obj - Object)
    (active ?obj)
    (off ?obj - Object)
    (can_open ?obj - Object)
    (grabbable ?obj - Object)
    (sittable ?obj - Object)
    (lieable ?obj - Object)
    (has_paper ?obj)
    (has_plug ?obj)
    (lookable ?obj - Object)
    (readable ?obj - Object)
    (eatable ?obj - Object)
    (clothes ?obj - Object)
    (containers ?obj - Object)
    (cuttable ?obj - Object)
    (drinkable ?obj - Object)
    (between ?obj1 - Object ?obj2 - Object)
    (hangable ?obj - Object)
    (surfaces ?obj - Object)
    (cover_object ?obj - Object)
    (cream ?obj - Object)
    (pourable ?obj - Object)
    (movable ?obj - Object)
    (recipient ?obj - Object)
    (on ?obj1 - Object ?obj2 - Object)
    (inside ?obj1 ?obj2)
    (facing ?obj1 - Object ?obj2 - Object)
    (holds_rh ?character - Character ?obj - Object)
    (holds_lh ?character - Character ?obj - Object)
    (sitting ?character)
    (close ?character ?object)
    (standing ?character)
    (has_switch ?object)
    (visible ?object)
    (hands_full ?character)
    (can_cook ?cont)
    (cooked ?obj ?cont)
  )

  ; Actions
    (:action walk
        :parameters (?character - Character ?obj1 - Object)
        :precondition (and (standing ?character) (visible ?obj1))
        :effect (and (close ?character ?obj1)
                    ;(forall (?obj - object) (when (visible ?obj) (not (visible ?obj))))
                    (visible ?obj1))
             )

    (:action walk
        :parameters (?character - Character ?room - Room)
        :precondition (standing ?character)
        :effect (and
                   (inside ?character ?room)
                   (close ?character ?room)))

    (:action grab
        :parameters (?character - Character ?object - Object)
        :precondition (and (grabbable ?object) (close ?character ?object) (visible ?object) (not (hands_full ?character)))
        :effect (and (holds_rh ?character ?object)
                      (hands_full ?character)
                      (forall (?cont - Object)

                            (and (not (inside ?object ?cont)) (not (on ?object ?cont)))
                     )
                )
        )

    (:action switchon
        :parameters (?character - Character ?object - Object)
        :precondition (and (has_switch ?object) (off ?object) (close ?character ?object) (visible ?object) (not (hands_full ?character)))
        :effect (active ?object))

    (:action switchoff
        :parameters (?character - Character ?object - Object)
        :precondition (and (has_switch ?object) (active ?object) (close ?character ?object) (visible ?object) (not (hands_full ?character)))
        :effect (off ?object))

    (:action put
        :parameters (?character - Character ?object - Object ?target - Surface)
        :precondition (and (holds_rh ?character ?object) (close ?character ?target))
        :effect (and (not (holds_rh ?character ?object)) (on ?object ?target) (not (hands_full ?character))) )

    (:action putin
        :parameters (?character - Character
                      ?object - Object
                      ?container - Object)
        :precondition (and (holds_rh ?character ?object) (close ?character ?container) (open ?container))
        :effect (and (not (holds_rh ?character ?object)) (inside ?object ?container) (not (hands_full ?character))))

    (:action scanroom
        :parameters (?character - Character ?obj - Object ?room - Room)
        :precondition (and (inside ?character ?room))
        :effect (and
            (when (inside ?obj ?room) (visible ?obj))
        )
    )


    (:action open
        :parameters (?character - Character
                     ?container)
        :precondition (and (close ?character ?container)
                        (closed ?container)
                        (visible ?container)
                       )
        :effect (and (open ?container)
                    (forall (?obj - Object)
                        (when (inside ?obj ?container)
                            (visible ?obj)
                        )
                    )
                    (not (closed ?container))
                )
     )

    (:action close
        :parameters (?character - Character
                     ?container)
        :precondition (and (close ?character ?container) (open ?container) (visible ?container))
        :effect (and (closed ?container)
                    (not (open ?container))
                    (forall (?obj - Object)
                                (when (inside ?obj ?container)
                                    (not(visible ?obj))
                                )
                    )
         )
    )

    (:action cook
        :parameters (?obj ?cont)
        :precondition (and
                        (inside ?obj ?cont)
                        (can_cook ?cont)
                        (can_open ?cont)
                        (has_switch ?cont)
                        (closed ?cont)
                        (active ?cont)
                      )
        :effect (and
                  (cooked ?obj ?cont)
                )
      )
)
