/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "segmentInCircumferenceModule.hpp"
#include "keynodes/CircumferenceKeynodes.hpp"
#include "agents/TwoChordsAgent.hpp"
#include "agents/CalculateSegmentInCircumferenceAgent.hpp"

using namespace segmentInCircumferenceModule;

SC_IMPLEMENT_MODULE(SegmentInCircumferenceModule)

sc_result SegmentInCircumferenceModule::InitializeImpl()
{
  if (!segmentInCircumferenceModule::CircumferenceKeynodes::InitGlobal())
    return SC_RESULT_ERROR;

  SC_AGENT_REGISTER(TwoChordsAgent)
  SC_AGENT_REGISTER(CalculateSegmentInCircumferenceAgent)

  return SC_RESULT_OK;
}

sc_result SegmentInCircumferenceModule::ShutdownImpl()
{
  SC_AGENT_UNREGISTER(TwoChordsAgent)
  SC_AGENT_UNREGISTER(CalculateSegmentInCircumferenceAgent)


  return SC_RESULT_OK;
}
