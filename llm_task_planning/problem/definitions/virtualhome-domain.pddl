(define (domain virtualhome-simulator)
  (:requirements :strips :typing)

  (:types
    character object room
  )

    (:predicates
        (CAN_OPEN ?o - object)
        (CLOTHES ?o - object)
        (CONTAINERS ?o - object)
        (COVER_OBJECT ?o - object)
        (CREAM ?o - object)
        (CUTTABLE ?o - object)
        (DRINKABLE ?o - object)
        (EATABLE ?o - object)
        (GRABBABLE ?o - object) ; Whether the object can be grabbed
        (HANGABLE ?o - object)
        (HAS_PAPER ?o - object)
        (HAS_PLUG ?o - object)
        (HAS_SWITCH ?o - object) ; Whether the object can be turned on or off
        (LIEABLE ?o - object)
        (LOOKABLE ?o - object)
        (MOVABLE ?o - object)
        (POURABLE ?o - object)
        (READABLE ?o - object)
        (RECIPIENT ?o - object)
        (SITTABLE ?o - object) ; Whether the agent can sit in this object
        (SURFACE ?o - object) ; Whether the agent can place things on this object

        (ON ?o1 - object ?o2 - object)
        (INSIDE ?o1 - object ?o2 - object)
        (INSIDE ?o1 - object ?r - room)
        (INSIDE ?char - character ?r - room)
        (BETWEEN ?o - object ?r - room) ; for doors
        (CLOSE ?char - character ?o - object) ; char is close to o (< 1.5 metres).
        (CLOSE ?o - object ?o - object) ;
        (FACING ?char - object ?o - object) ; o is visible from char and distance is < 5 metres. If char is a sofa or a chair it should also be turned towards o.
        (HOLDS_RH ?char - character ?o - object) ; char holds o with the right hand.
        (HOLDS_LH ?char - character ?o - object) ; char holds o with the left hand.
        (SITTING ?char - character ?o - object) ; char is sitting in o.
        (OPEN ?o - object)
        (CLOSED ?o - object)
        (ON ?o - object)
        (OFF ?o - object)
    )
    (:action walk
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (not (SITTING ?char ?o))
            (or (not (INSIDE ?obj1 ?o))
                (INSIDE ?char ?obj1))
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
        )
        :effect (and
            (CLOSE ?char ?obj1)
            (FACING ?char ?obj1)
        )
    )

    (:action run
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (not (SITTING ?char ?o))
            (or (not (INSIDE ?obj1 ?o))
                (INSIDE ?char ?obj1))
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
        )
        :effect (and
            (CLOSE ?char ?obj1)
            (FACING ?char ?obj1)
        )
    )

    (:action sit
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (not (SITTING ?char ?o))
            (CLOSE ?char ?obj1)
            (SITTABLE ?obj1)
        )
        :effect (SITTING ?char ?obj1)
    )

    (:action standup
        :parameters (?char - character)
        :precondition (SITTING ?char ?o)
        :effect (not (SITTING ?char ?o))
    )

    (:action grab
    :parameters (?char - character ?obj1 - object)
    :precondition (and
        (GRABBABLE ?obj1)
        (CLOSE ?char ?obj1)
        (not (INSIDE ?obj1 ?o))
        (or
            (not (HOLDS_RH ?char ?any_obj))
            (not (HOLDS_LH ?char ?any_obj)))
    )
    :effect (and
        (HOLDS_RH ?char ?obj1)
        (not (ON ?obj1 ?o2))
        (not (INSIDE ?obj1 ?o3))
    )
)

    (:action open
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (CAN_OPEN ?obj1)
            (CLOSED ?obj1)
            (CLOSE ?char ?obj1)
            (not (INSIDE ?obj1 ?o))
            (or (not (HOLDS_RH ?char ?any_obj))
                (not (HOLDS_LH ?char ?any_obj)))
        )
        :effect (OPEN ?obj1)
    )

    (:action close
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (CAN_OPEN ?obj1)
            (OPEN ?obj1)
            (CLOSE ?char ?obj1)
            (not (INSIDE ?obj1 ?o))
            (or (not (HOLDS_RH ?char ?any_obj))
                (not (HOLDS_LH ?char ?any_obj)))
        )
        :effect (CLOSED ?obj1)
    )

    (:action put
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (and
            (or (HOLDS_RH ?char ?obj1)
                (HOLDS_LH ?char ?obj1))
            (CLOSE ?char ?obj2)
        )
        :effect (and
            (ON ?obj1 ?obj2)
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
        )
    )

    (:action putin
        :parameters (?char - character ?obj1 - object ?obj2 - object)
        :precondition (and
            (or (HOLDS_RH ?char ?obj1)
                (HOLDS_LH ?char ?obj1))
            (CLOSE ?char ?obj2)
            (not (CLOSED ?obj2))
        )
        :effect (and
            (INSIDE ?obj1 ?obj2)
            (not (HOLDS_RH ?char ?obj1))
            (not (HOLDS_LH ?char ?obj1))
        )
    )

    (:action switchon
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (HAS_SWITCH ?obj1)
            (OFF ?obj1)
            (CLOSE ?char ?obj1)
        )
        :effect (ON ?obj1)
    )

    (:action switchoff
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (HAS_SWITCH ?obj1)
            (ON ?obj1)
            (CLOSE ?char ?obj1)
        )
        :effect (OFF ?obj1)
    )

    (:action drink
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (or (DRINKABLE ?obj1)
                (RECIPIENT ?obj1))
            (CLOSE ?char ?obj1)
        )
        :effect ()
    )

    (:action touch
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (CLOSE ?char ?obj1)
            (not (INSIDE ?obj1 ?o))
        )
        :effect ()
    )

    (:action lookat
        :parameters (?char - character ?obj1 - object)
        :precondition (and
            (FACING ?char ?obj1)
            (not (INSIDE ?obj1 ?o))
        )
        :effect ()
    )
)