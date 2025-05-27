#include <chrono>
#include <thread>
#include <cmath>
#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>
#include <factory/InferenceManagerFactory.hpp>
#include <agent/DirectInferenceAgent.hpp>
#include <inferenceConfig/InferenceConfig.hpp>
#include "CalculateSegmentInCircumferenceAgent.hpp"


using namespace std;
using namespace utils;

namespace segmentInCircumferenceModule {
    SC_AGENT_IMPLEMENTATION(CalculateSegmentInCircumferenceAgent) {
        SC_LOG_INFO("CalculateCircunferenceAgent: started");
        std::this_thread::sleep_for(std::chrono::seconds(3));
        ScAddr addr = otherAddr;
        ScAddr const &keynode_rrel_1 = m_memoryCtx.HelperFindBySystemIdtf("rrel_1");
        SC_LOG_INFO("CalculateCircunferenceAgent:try to output capture");
        ScAddr output = IteratorUtils::getAnyFromSet(&m_memoryCtx, IteratorUtils::getAnyByOutRelation(
                                                         &m_memoryCtx, addr, keynode_rrel_1));

        ScAddr unknownClass = m_memoryCtx.HelperFindBySystemIdtf("concept_unknowm_value");
        ScAddr lenValue;

        ScIterator3Ptr it3 = m_memoryCtx.Iterator3(unknownClass,
                                                   ScType::EdgeAccessConstPosPerm,
                                                   ScType::NodeConstClass);
        while (it3->Next()) {
            if (m_memoryCtx.HelperCheckEdge(output, it3->Get(2), ScType::EdgeAccessConstPosPerm)) {
                lenValue = it3->Get(2);
                SC_LOG_INFO("CalculateCircunferenceAgent:len captured");
                break;
            }
        }
        SC_LOG_INFO("CalculateCircunferenceAgent:"<<m_memoryCtx.HelperGetSystemIdtf(lenValue));
        double val=1;
        it3=m_memoryCtx.Iterator3(output, ScType::EdgeAccessConstPosPerm, ScType::NodeConstTuple);
        while (it3->Next()) {
            if (!m_memoryCtx.HelperCheckEdge(it3->Get(2),lenValue, ScType::EdgeAccessConstPosPerm)) {
                ScIterator3Ptr it=m_memoryCtx.Iterator3(it3->Get(2),ScType::EdgeAccessConstPosPerm, ScType::NodeConstClass);
                while (it->Next()) {
                    val*=std::stod(m_memoryCtx.HelperGetSystemIdtf(it->Get(2)));
                }
            }else {
                ScIterator3Ptr it=m_memoryCtx.Iterator3(it3->Get(2),ScType::EdgeAccessConstPosPerm, ScType::NodeConstClass);
                while (it->Next()) {
                   if (it->Get(2).Hash()!=lenValue.Hash()) {
                       val=val/std::stod(m_memoryCtx.HelperGetSystemIdtf(it->Get(2)));
                   }
                }
            }
            SC_LOG_INFO("val: "<<val);
        }
       if ( m_memoryCtx.HelperSetSystemIdtf(std::to_string(val),lenValue)) {
           SC_LOG_INFO("yeah");
       }else {
           SC_LOG_INFO(":(");
       }

        // ScAddr length=m_memoryCtx.HelperFindBySystemIdtf("length");

        //  it3=m_memoryCtx.Iterator3(circumference,
        //     ScType::EdgeAccessConstPosPerm,
        //     ScType::NodeConstClass);
        // while (it3->Next()) {
        //     if (m_memoryCtx.HelperCheckEdge(output,it3->Get(2),ScType::EdgeAccessConstPosPerm)) {
        //         double circum=std::stod(m_memoryCtx.HelperGetSystemIdtf(lenValue))*M_PI;
        //         m_memoryCtx.HelperSetSystemIdtf(std::to_string(circum),it3->Get(2));
        //         break;
        //     }
        // }
        SC_LOG_INFO("CalculateCircunferenceAgent: finished");
        utils::AgentUtils::finishAgentWork(&m_memoryCtx, addr,
                                           {}, true);
        return SC_RESULT_OK;
    }
} // namespace segmentInCircumferenceModule
