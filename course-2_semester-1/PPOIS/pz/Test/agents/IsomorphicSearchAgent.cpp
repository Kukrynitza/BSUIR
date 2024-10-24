#include <iostream>

#include <sc-memory/sc_memory.hpp>
#include <sc-memory/sc_stream.hpp>
#include <sc-memory/sc_template_search.cpp>

#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>

#include "IsomorphicSearchAgent.hpp"

using namespace std;
using namespace utils;

namespace exampleModule
{
SC_AGENT_IMPLEMENTATION(IsomorphicSearchAgent)
{
  SC_LOG_DEBUG("IsomorphicSearchAgent: started");
  ScAddr actionNode = otherAddr;
  SC_LOG_INFO("Hello world Samurai");
return SC_RESULT_OK;
}

}