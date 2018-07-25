from approximate_confluent_flow import OnePlusLogTwoApproximation, OnePlusLnApproximation
from fractional_integral_flow import ConfluentFlow, SplittableFlow
from simple_mechanisms import GreedyNewestDelegate, GreedyRandomDelegation, GreedyPowerOfChoice, NoChoice, \
    GeneralizedPowerOfChoice

MECHANISMS_LIST = [NoChoice, GreedyNewestDelegate, GreedyPowerOfChoice, GreedyRandomDelegation, ConfluentFlow,
                   SplittableFlow, OnePlusLogTwoApproximation, OnePlusLnApproximation, GeneralizedPowerOfChoice]
MECHANISMS = {m.PLOT_ABBREVIATION: m for m in MECHANISMS_LIST}


def describe_mechanisms(including_single):
    descriptions = []
    for m in MECHANISMS_LIST:
        if m is NoChoice and not including_single:
            continue
        descriptions.append(f"{m.PLOT_ABBREVIATION}: {m.PLOT_LABEL};")

    return "\n".join(descriptions)


def parse_mechanisms(argument, allow_single):
    single_mechanisms = []
    mechanisms = []

    for x in argument:
        if MECHANISMS[x] is NoChoice:
            if not allow_single:
                exit(f"Single delegation is not allowed in this script. Call with '-h' for usage.")
            else:
                single_mechanisms.append(MECHANISMS[x])
                continue
        if x not in MECHANISMS:
            exit(f"Invalid mechanism designation '{x}'. Call with '-h' for usage.")
        else:
            mechanisms.append(MECHANISMS[x])

    if allow_single:
        return single_mechanisms, mechanisms
    else:
        return mechanisms
