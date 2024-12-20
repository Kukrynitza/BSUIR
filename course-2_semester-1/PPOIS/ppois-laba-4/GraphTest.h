#include <gtest/gtest.h>
#include "Graph.h"

TEST(GraphTest, AddNode) {
    Graph<int> graph;

    // Add nodes
    graph.addNode(1);
    graph.addNode(2);
    graph.addNode(3);

    // Check the number of nodes
    EXPECT_EQ(graph.getNodeCount(), 3);

    // Check if specific nodes exist
    EXPECT_TRUE(graph.containsNode(1));
    EXPECT_TRUE(graph.containsNode(2));
    EXPECT_TRUE(graph.containsNode(3));
    EXPECT_FALSE(graph.containsNode(4));
}

TEST(GraphTest, AddEdge) {
    Graph<int> graph;

    // Add nodes and edges
    graph.addNode(1);
    graph.addNode(2);
    graph.addEdge(1, 2);

    // Check the number of edges
    EXPECT_EQ(graph.getEdgeCount(), 1);

    // Check if the edge exists
    EXPECT_TRUE(graph.containsEdge(1, 2));
    EXPECT_FALSE(graph.containsEdge(2, 1));
}

TEST(GraphTest, RemoveNode) {
    Graph<int> graph;

    // Add nodes and edges
    graph.addNode(1);
    graph.addNode(2);
    graph.addEdge(1, 2);

    // Remove a node
    graph.removeNode(2);

    // Check the number of nodes
    EXPECT_EQ(graph.getNodeCount(), 1);

    // Check if the edge was removed along with the node
    EXPECT_FALSE(graph.containsEdge(1, 2));
}

TEST(GraphTest, RemoveNonExistentNode) {
    Graph<int> graph;

    // Add nodes
    graph.addNode(1);

    // Try to remove a non-existent node
    EXPECT_THROW(graph.removeNode(2), std::invalid_argument);
}

TEST(GraphTest, ContainsNodeAndEdge) {
    Graph<int> graph;

    // Add nodes and edges
    graph.addNode(1);
    graph.addNode(2);
    graph.addEdge(1, 2);

    // Check for nodes and edges
    EXPECT_TRUE(graph.containsNode(1));
    EXPECT_TRUE(graph.containsNode(2));
    EXPECT_FALSE(graph.containsNode(3));

    EXPECT_TRUE(graph.containsEdge(1, 2));
    EXPECT_FALSE(graph.containsEdge(2, 1));
}

TEST(GraphTest, NodeDegree) {
    Graph<int> graph;

    // Add nodes and edges
    graph.addNode(1);
    graph.addNode(2);
    graph.addNode(3);
    graph.addEdge(1, 2);
    graph.addEdge(1, 3);

    // Check node degrees
    EXPECT_EQ(graph.getNodeDegree(1), 2);
    EXPECT_EQ(graph.getNodeDegree(2), 0);
    EXPECT_EQ(graph.getNodeDegree(3), 0);
}

TEST(GraphTest, ClearGraph) {
    Graph<int> graph;

    // Add nodes and edges
    graph.addNode(1);
    graph.addNode(2);
    graph.addEdge(1, 2);

    // Clear the graph
    graph.clear();

    // Check if the graph is empty
    EXPECT_TRUE(graph.empty());
    EXPECT_EQ(graph.getNodeCount(), 0);
    EXPECT_EQ(graph.getEdgeCount(), 0);
}

TEST(GraphTest, CopyConstructor) {
    Graph<int> graph;

    // Add nodes and edges
    graph.addNode(1);
    graph.addNode(2);
    graph.addEdge(1, 2);

    // Copy the graph
    Graph<int> copiedGraph = graph;

    // Check if the copy matches the original
    EXPECT_EQ(copiedGraph.getNodeCount(), graph.getNodeCount());
    EXPECT_EQ(copiedGraph.getEdgeCount(), graph.getEdgeCount());
    EXPECT_TRUE(copiedGraph.containsEdge(1, 2));
    EXPECT_TRUE(copiedGraph.containsNode(1));
    EXPECT_TRUE(copiedGraph.containsNode(2));
}

TEST(GraphTest, AssignmentOperator) {
    Graph<int> graph1;

    // Add nodes and edges to the first graph
    graph1.addNode(1);
    graph1.addNode(2);
    graph1.addEdge(1, 2);

    Graph<int> graph2;

    // Add nodes to the second graph
    graph2.addNode(3);

    // Assign the first graph to the second
    graph2 = graph1;

    // Check if the assignment worked
    EXPECT_EQ(graph2.getNodeCount(), graph1.getNodeCount());
    EXPECT_EQ(graph2.getEdgeCount(), graph1.getEdgeCount());
    EXPECT_TRUE(graph2.containsEdge(1, 2));
    EXPECT_TRUE(graph2.containsNode(1));
    EXPECT_TRUE(graph2.containsNode(2));
    EXPECT_FALSE(graph2.containsNode(3));
}

TEST(GraphTest, EqualityOperator) {
    Graph<int> graph1;
    Graph<int> graph2;

    // Add nodes and edges
    graph1.addNode(1);
    graph1.addNode(2);
    graph1.addEdge(1, 2);

    graph2.addNode(1);
    graph2.addNode(2);
    graph2.addEdge(1, 2);

    // Check equality
    EXPECT_TRUE(graph1 == graph2);

    // Modify one graph
    graph2.addNode(3);

    // Check inequality
    EXPECT_FALSE(graph1 == graph2);
}

