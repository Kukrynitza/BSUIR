#include <cmath>
#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>
#include <factory/InferenceManagerFactory.hpp>
#include <agent/DirectInferenceAgent.hpp>
#include <inferenceConfig/InferenceConfig.hpp>
#include "TwoChordsAgent.hpp"

#include "sc-memory/sc_struct.hpp"

using namespace std;
using namespace utils;


namespace segmentInCircumferenceModule {
    SC_AGENT_IMPLEMENTATION(TwoChordsAgent) {
        SC_LOG_INFO("TwoChordsAgent: started");
        ScAddrVector res;
        ScAddr addr = otherAddr;
        ScAddr const &keynode_rrel_1 = m_memoryCtx.HelperFindBySystemIdtf("rrel_1");
        ScAddr const &keynode_rrel_2 = m_memoryCtx.HelperFindBySystemIdtf("rrel_2");
        ScAddr const &keynode_rrel_3 = m_memoryCtx.HelperFindBySystemIdtf("rrel_3");

        ScAddr const output = IteratorUtils::getAnyByOutRelation(
            &m_memoryCtx, addr, keynode_rrel_3);

        SC_LOG_INFO("TwoChordsAgent: output captured");
        ScAddr const rules = IteratorUtils::getAnyByOutRelation(
            &m_memoryCtx, addr, keynode_rrel_2);
        ScAddr const input = IteratorUtils::getAnyByOutRelation(
            &m_memoryCtx, addr, keynode_rrel_1);
        bool prevResult = false;
        ScIterator3Ptr it3 = m_memoryCtx.Iterator3(output,
                                                   ScType::EdgeAccessConstPosPerm,
                                                   ScType::NodeConstStruct);
        if (it3->Next()) {
            prevResult = true;
        }
        if (!prevResult) {
            ScAddr newOutputStructure = m_memoryCtx.CreateNode(ScType::NodeConstStruct);
            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, output, newOutputStructure);
            ScAddrVector inputStructure = {input};
            ScAddrVector arguments = {

            };
            ScAddr circleClass = m_memoryCtx.HelperFindBySystemIdtf("concept_circle");
            it3 = m_memoryCtx.Iterator3(circleClass,
                                        ScType::EdgeAccessConstPosPerm,
                                        ScType::NodeConst);
            while (it3->Next()) {
                if (m_memoryCtx.HelperCheckEdge(input, it3->Get(2), ScType::EdgeAccessConstPosPerm)) {
                    arguments.push_back(it3->Get(2));
                }
            }
            ScAddr pointClass = m_memoryCtx.HelperFindBySystemIdtf("concept_point");
            it3 = m_memoryCtx.Iterator3(pointClass,
                                        ScType::EdgeAccessConstPosPerm,
                                        ScType::NodeConst
            );
            while (it3->Next()) {
                if (m_memoryCtx.HelperCheckEdge(input, it3->Get(2), ScType::EdgeAccessConstPosPerm)) {
                    arguments.push_back(it3->Get(2));
                }
            }
            int amnt = 0;
            ScAddr segmentClass = m_memoryCtx.HelperFindBySystemIdtf("concept_segment");
            it3 = m_memoryCtx.Iterator3(segmentClass,
                                        ScType::EdgeAccessConstPosPerm,
                                        ScType::NodeConst
            );
            while (it3->Next()) {
                if (m_memoryCtx.HelperCheckEdge(input, it3->Get(2), ScType::EdgeAccessConstPosPerm)) {
                    arguments.push_back(it3->Get(2));
                    amnt++;
                }
            }

            ScAddr const &outputStructure = m_memoryCtx.CreateNode(ScType::NodeConstStruct);
            InferenceParams const &inferenceParams{rules, arguments, inputStructure, outputStructure};

            InferenceConfig const &inferenceConfig{
                GENERATE_UNIQUE_FORMULAS, REPLACEMENTS_ALL, TREE_FULL,
                SEARCH_ONLY_ACCESS_EDGES_IN_STRUCTURES, GENERATED_ONLY, SEARCH_WITH_REPLACEMENTS
            };
            std::unique_ptr<inference::InferenceManagerAbstract> inferenceManager =
                    inference::InferenceManagerFactory::constructDirectInferenceManagerAll(
                        &m_memoryCtx, inferenceConfig);
            SC_LOG_INFO("TwoChordsAgent: everything ready");
            bool result = inferenceManager->applyInference(inferenceParams);
            inference::SolutionTreeManager manager(&m_memoryCtx);
            ScAddr const &solution = manager.createSolution(outputStructure, result);


            SC_LOG_INFO("Inference passed");
            it3 = m_memoryCtx.Iterator3(
                solution,
                ScType::EdgeDCommonConst,
                ScType::NodeConst
            );
            if (it3->Next()) {




                SC_LOG_INFO("output structure hash "<<it3->Get(2).Hash());
                std::set<uint64_t> scSet;
                ScAddr out = it3->Get(2);
                ScIterator3Ptr it3set = m_memoryCtx.Iterator3(out,
                                                              ScType::EdgeAccessConstPosPerm,
                                                              ScType::NodeConstTuple);
                while (it3set->Next()) {
                    bool check = false;
                    SC_LOG_INFO("chrck TUPLE");

                    it3 = m_memoryCtx.Iterator3(it3set->Get(2),
                                                ScType::EdgeAccessConstPosPerm,
                                                ScType::NodeConstClass);
                    while (it3->Next()) {
                        if (scSet.find(it3->Get(2).Hash()) == scSet.end()) {
                            scSet.insert(it3->Get(2).Hash());
                            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, newOutputStructure, it3->Get(2));
                            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, newOutputStructure, it3->Get(1));

                            check = true;
                        }
                    }
                    if (check) {
                        m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, newOutputStructure, it3set->Get(2));
                        it3 = m_memoryCtx.Iterator3(it3set->Get(2),
                                                    ScType::EdgeDCommonConst,
                                                    ScType::NodeConstClass
                        );
                        while (it3->Next()) {
                            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, newOutputStructure, it3->Get(1));
                            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, newOutputStructure, it3->Get(2));
                        }
                        SC_LOG_INFO("TUPLE");
                    }
                }
                it3set = m_memoryCtx.Iterator3(out,
                                               ScType::EdgeAccessConstPosPerm,
                                               ScType::NodeConstNoRole);
                while (it3set->Next()) {
                    m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, newOutputStructure, it3set->Get(2));
                    it3 = m_memoryCtx.Iterator3(it3set->Get(2),
                                                ScType::EdgeAccessConstPosPerm,
                                                ScType::EdgeDCommonConst);
                    while (it3->Next()) {
                        if (m_memoryCtx.
                            HelperCheckEdge(newOutputStructure, it3->Get(2), ScType::EdgeAccessConstPosPerm)) {
                            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, newOutputStructure, it3->Get(1));
                        }
                    }
                }
            }
        }


        SC_LOG_INFO("TwoChordsAgent: finished");


        utils::AgentUtils::finishAgentWork(&m_memoryCtx, addr,
                                           res, true);
        return SC_RESULT_OK;
    }
} // namespace segmentInCircumferenceModule
