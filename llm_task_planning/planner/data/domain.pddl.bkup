(define (domain virtual-home)
(:requirements :strips :typing :equality :disjunctive-preconditions :conditional-effects)
(:types Character
      Object
      Room
      Surface - Object
      Container - Surface
)

  (:predicates
    ; States
    (open ?obj - Container)
    (closed ?obj - Container)
    (active ?obj)
    (off ?obj - Object)
    (can_open ?obj - Object)
    (grabbable ?obj - Object)
    (sittable ?obj - Object)
    (on ?obj1 - Object ?obj2 - Surface)
    (inside ?obj1 ?obj2)
    (facing ?obj1 - Object ?obj2 - Object)
    (holds_rh ?character - Character ?obj - Object)
    (holds_lh ?character - Character ?obj - Object)
    (sitting ?character)
    (close ?character ?object)
    (standing ?character)
    (has_switch ?object)
    (visible ?object)
  )

  ; Actions
    (:action walk
        :parameters (?character - Character ?obj - Object)
        :precondition (and (standing ?character) (visible ?obj))
        :effect (close ?character ?obj))

    (:action walk
        :parameters (?character - Character ?room - Room)
        :precondition (standing ?character)
        :effect (and (inside ?character ?room) (close ?character ?room)))

    (:action grab
        :parameters (?character - Character ?object - Object)
        :precondition (and (grabbable ?object) (close ?character ?object) (visible ?object))
        :effect (holds_rh ?character ?object))

    (:action switchon
        :parameters (?character - Character ?object - Object)
        :precondition (and (has_switch ?object) (off ?object) (close ?character ?object) (visible ?object))
        :effect (active ?object))

    (:action switchoff
        :parameters (?character - Character ?object - Object)
        :precondition (and (has_switch ?object) (active ?object) (close ?character ?object) (visible ?object))
        :effect (off ?object))

    (:action put
        :parameters (?character - Character ?object - Object ?target - Surface)
        :precondition (and (holds_rh ?character ?object) (close ?character ?target))
        :effect (and (not (holds_rh ?character ?object)) (on ?object ?target)))

    (:action putin
        :parameters (?character - Character
                      ?object - Object
                      ?container - Container)
        :precondition (and (holds_rh ?character ?object) (close ?character ?container) (open ?container))
        :effect (and (not (holds_rh ?character ?object)) (inside ?object ?container)))

    (:action scanroom
        :parameters (?character - Character ?obj - Object ?room - Room)
        :precondition (and (inside ?character ?room))
        :effect (and
            (when (inside ?obj ?room) (visible ?obj))
        )
)


    (:action open
        :parameters (?character - Character
                     ?container - Container
                     ?object - Object)
        :precondition (and (close ?character ?container) (closed ?container) (visible ?container))
        :effect (and (open ?container) (when (inside ?object ?container) (visible ?object))))

    (:action close
        :parameters (?character - Character
                     ?container - Container)
        :precondition (and (close ?character ?container) (open ?container) (visible ?container))
        :effect (not (open ?container)))
)
