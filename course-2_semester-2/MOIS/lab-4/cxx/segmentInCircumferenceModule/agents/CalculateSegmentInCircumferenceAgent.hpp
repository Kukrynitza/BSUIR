#pragma once

#include "TwoChordsAgent.hpp"

#include "CalculateSegmentInCircumferenceAgent.generated.hpp"
namespace segmentInCircumferenceModule {
  class CalculateSegmentInCircumferenceAgent : public ScAgent {
    SC_CLASS(Agent, Event(CircumferenceKeynodes::action_calculate_segment, ScEvent::Type::AddOutputEdge))
    SC_GENERATED_BODY()
private:
    ScAddr callingTheDirectInferenceAgent( ScAddr const & inputStr,ScAddr const & rules_set,ScAddr const structureToSet);
  };

} // namespace segmentInCircumferenceModule