from api.main import _decision_from_gap


def test_balanced_marketplace_requires_no_intervention():
    actions = _decision_from_gap(-2)
    assert actions[0]["action"] == "no_capacity_intervention"
    assert actions[0]["human_approval_required"] is False


def test_material_shortage_requires_approved_actions():
    actions = _decision_from_gap(12)
    names = {a["action"] for a in actions}
    assert {"availability_campaign", "expand_matching_radius", "incentive_simulation"} <= names
    assert all(a["human_approval_required"] for a in actions)
