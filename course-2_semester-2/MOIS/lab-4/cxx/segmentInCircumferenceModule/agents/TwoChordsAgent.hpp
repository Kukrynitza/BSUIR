#pragma once

#include <sc-memory/kpm/sc_agent.hpp>
#include "keynodes/CircumferenceKeynodes.hpp"

#include "TwoChordsAgent.generated.hpp"
namespace segmentInCircumferenceModule {
  class TwoChordsAgent : public ScAgent {
    SC_CLASS(Agent, Event(CircumferenceKeynodes::action_apply_theorem, ScEvent::Type::AddOutputEdge))
    SC_GENERATED_BODY()
private:

  };

} // namespace segmentInCircumferenceModule