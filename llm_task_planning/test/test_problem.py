from llm_task_planning.problem import PDDLProblem

def test_pddl_problem():
    test_problem = '''
  (define (domain pr2-tamp)
      (:requirements :strips :equality)
      (:constants base left right head)
      (:predicates
        (Arm ?a)
        (Graspable ?o)
        (Stackable ?o ?r)
        (Scannable ?r)
        (Registerable ?o)
        (Sink ?r)
        (Stove ?r)
    
        (Pose ?o ?p)
        (Grasp ?o ?g)
        (Kin ?a ?o ?p ?g ?q ?t)
        (BaseMotion ?q1 ?t ?q2)
        (Supported ?o ?p ?r)
        (Vis ?o ?p ?bq ?hq ?ht)
    
        (VisRange ?o ?p ?bq)
        (RegRange ?o ?p ?bq)
    
        (CanMove) ; TODO: include base
        (AtPose ?o ?p)
        (AtGrasp ?a ?o ?g)
        (HandEmpty ?a)
        (AtBConf ?q)
        (AtConf ?a ?q) ; TODO: a single conf predicate
    
        (On ?o ?r)
        (Holding ?a ?o)
    
        (Uncertain ?o)
        (Scanned ?o)
        (Localized ?o)
        (Registered ?o)
      )
      (:functions
        (MoveCost)
        (PickCost)
        (PlaceCost)
        (ScanCost)
        (LocalizeCost ?r ?o)
        (RegisterCost)
      )
    
      (:action move_base
        :parameters (?q1 ?q2 ?t)
        :precondition (and (BaseMotion ?q1 ?t ?q2)
                           (AtBConf ?q1)) ; (CanMove)
        :effect (and (AtBConf ?q2)
                     (not (AtBConf ?q1)) (not (CanMove))
                     (increase (total-cost) (MoveCost)))
                     ; (forall (?o) (not (Registered ?o))))
                     ; (forall (?o) (when (Graspable ?o) (not (Registered ?o)))))
      )
      (:action pick
        :parameters (?a ?o ?p ?g ?q ?t)
        :precondition (and (Kin ?a ?o ?p ?g ?q ?t)
                           (Registered ?o) (AtPose ?o ?p) (HandEmpty ?a) (AtBConf ?q))
        :effect (and (AtGrasp ?a ?o ?g) (CanMove)
                     (not (AtPose ?o ?p)) (not (HandEmpty ?a))
                     (increase (total-cost) (PickCost)))
      )
      (:action place
        :parameters (?a ?o ?p ?g ?q ?t)
        :precondition (and (Kin ?a ?o ?p ?g ?q ?t)
                           (AtGrasp ?a ?o ?g) (AtBConf ?q)) ; (Localized ?o)
        :effect (and (AtPose ?o ?p) (HandEmpty ?a) (CanMove)
                     (not (AtGrasp ?a ?o ?g))
                     (increase (total-cost) (PlaceCost)))
      )
    
      (:action scan
        :parameters (?o ?p ?bq ?hq ?ht)
        :precondition (and (Vis ?o ?p ?bq ?hq ?ht) (VisRange ?o ?p ?bq) (Scannable ?o)
                           (AtPose ?o ?p) (AtBConf ?bq) (Localized ?o))
        :effect (and (Scanned ?o) (CanMove)
                     (increase (total-cost) (ScanCost)))
      )
      (:action localize
        :parameters (?r ?p1 ?o ?p2)
        :precondition (and (Stackable ?o ?r) (Pose ?r ?p1) (Pose ?o ?p2) ; (FiniteScanCost ?r ?o)
                       (AtPose ?o ?p2) (Scanned ?r) (Uncertain ?o))
        :effect (and (Localized ?o) (Supported ?o ?p2 ?r)
                     (not (Uncertain ?o))
                     (increase (total-cost) (LocalizeCost ?r ?o)))
      )
      (:action register
        :parameters (?o ?p ?bq ?hq ?ht)
        :precondition (and (Vis ?o ?p ?bq ?hq ?ht) (RegRange ?o ?p ?bq) (Registerable ?o)
                           (AtPose ?o ?p) (AtBConf ?bq) (Localized ?o))
        :effect (and (Registered ?o) (CanMove)
                     (increase (total-cost) (RegisterCost)))
      )
    
      (:derived (On ?o ?r)
        (exists (?p) (and (Supported ?o ?p ?r)
                          (AtPose ?o ?p)))
      )
      (:derived (Holding ?a ?o)
        (exists (?g) (and (Arm ?a) (Grasp ?o ?g)
                          (AtGrasp ?a ?o ?g)))
      )
    )
    '''
    problem = PDDLProblem()
    problem.parse_problem(test_problem)
    problem.display()

test_pddl_problem()

