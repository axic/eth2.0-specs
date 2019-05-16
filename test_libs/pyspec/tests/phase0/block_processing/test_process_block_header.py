from copy import deepcopy
import pytest


# mark entire file as 'header'
pytestmark = pytest.mark.header


def prepare_state_for_header_processing(spec, helpers, state):
    spec.process_slot(state)
    helpers.advance_slot(state)


def run_block_header_processing(spec, helpers, state, block, valid=True):
    """
    Run ``spec.process_block_header`` returning the pre and post state.
    If ``valid == False``, run expecting ``AssertionError``
    """
    prepare_state_for_header_processing(spec, helpers, state)
    post_state = deepcopy(state)

    if not valid:
        with pytest.raises(AssertionError):
            spec.process_block_header(post_state, block)
        return state, None

    spec.process_block_header(post_state, block)
    return state, post_state


def test_success(spec, helpers, state):
    block = helpers.build_empty_block_for_next_slot(state)
    pre_state, post_state = run_block_header_processing(spec, helpers, state, block)
    return state, block, post_state


def test_invalid_slot(spec, helpers, state):
    block = helpers.build_empty_block_for_next_slot(state)
    block.slot = state.slot + 2  # invalid slot

    pre_state, post_state = run_block_header_processing(spec, helpers, state, block, valid=False)
    return pre_state, block, None


def test_invalid_parent_block_root(spec, helpers, state):
    block = helpers.build_empty_block_for_next_slot(state)
    block.parent_root = b'\12' * 32  # invalid prev root

    pre_state, post_state = run_block_header_processing(spec, helpers, state, block, valid=False)
    return pre_state, block, None


def test_proposer_slashed(spec, helpers, state):
    # use stub state to get proposer index of next slot
    stub_state = deepcopy(state)
    helpers.next_slot(stub_state)
    proposer_index = spec.get_beacon_proposer_index(stub_state)

    # set proposer to slashed
    state.validator_registry[proposer_index].slashed = True

    block = helpers.build_empty_block_for_next_slot(state)

    pre_state, post_state = run_block_header_processing(spec, helpers, state, block, valid=False)
    return pre_state, block, None