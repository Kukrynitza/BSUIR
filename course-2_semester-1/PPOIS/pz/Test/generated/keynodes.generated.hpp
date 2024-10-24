#include <memory>

#include "sc-memory/sc_memory.hpp"


#include "sc-memory/sc_event.hpp"




#define keynodes_hpp_19_init  bool _InitInternal(ScAddr const & outputStructure = ScAddr::Empty) override \
{ \
    ScMemoryContext ctx(sc_access_lvl_make_min, "Keynodes::_InitInternal"); \
    ScSystemIdentifierQuintuple fiver; \
    bool result = true; \
    return result; \
}


#define keynodes_hpp_19_initStatic static bool _InitStaticInternal(ScAddr const & outputStructure = ScAddr::Empty)  \
{ \
    ScMemoryContext ctx(sc_access_lvl_make_min, "Keynodes::_InitStaticInternal"); \
    ScSystemIdentifierQuintuple fiver; \
    bool result = true; \
	ctx.HelperResolveSystemIdtf("action_test", ScType::NodeConst, fiver);action_test = fiver.addr1; result = result && action_test.IsValid(); if (outputStructure.IsValid()) {ctx.CreateEdge(ScType::EdgeAccessConstPosPerm, outputStructure, fiver.addr1);ctx.CreateEdge(ScType::EdgeAccessConstPosPerm, outputStructure, fiver.addr2);ctx.CreateEdge(ScType::EdgeAccessConstPosPerm, outputStructure, fiver.addr3);ctx.CreateEdge(ScType::EdgeAccessConstPosPerm, outputStructure, fiver.addr4);}; \
    return result; \
}


#define keynodes_hpp_19_decl 

#define keynodes_hpp_Keynodes_impl 

#undef ScFileID
#define ScFileID keynodes_hpp

