#include "Graph.h"
using namespace std;
                        int main() {
                            Graph<int> graph;
                            int choice, from, to, value;

                            do {
                                 cout << "\nMenu:\n";
                                 cout << "1. Add node\n";
                                 cout << "2. Add edge\n";
                                 cout << "3. Remove node\n";
                                 cout << "4. Remove edge\n";
                                 cout << "5. Check if node exists\n";
                                 cout << "6. Check if edge exists\n";
                                 cout << "7. Get node count\n";
                                 cout << "8. Get edge count\n";
                                 cout << "9. Get node degree\n";
                                 cout << "10. Print graph\n";
                                 cout << "11. Iterate over nodes\n";
                                 cout << "12. Iterate over edges\n";
                                 cout << "13. Remove node by iterator\n";
                                 cout << "14. Remove edge by iterator\n";
                                 cout << "15. Iterate over adjacent nodes\n";
                                 cout << "0. Exit\n";
                                 cout << "Enter your choice: ";
                                 cin >> choice;

                                try {
                                    switch (choice) {
                                    case 1:
                                         cout << "Enter node value: ";
                                         cin >> value;
                                        graph.addNode(value);
                                        break;
                                    case 2:
                                         cout << "Enter from node: ";
                                         cin >> from;
                                         cout << "Enter to node: ";
                                         cin >> to;
                                        graph.addEdge(from, to);
                                        break;
                                    case 3:
                                         cout << "Enter node value: ";
                                         cin >> value;
                                        graph.removeNode(value);
                                        break;
                                    case 4:
                                         cout << "Enter from node: ";
                                         cin >> from;
                                         cout << "Enter to node: ";
                                         cin >> to;
                                        graph.removeEdge(from, to);
                                        break;
                                    case 5:
                                         cout << "Enter node value: ";
                                         cin >> value;
                                         cout << "Node " << value << (graph.containsNode(value) ? " exists" : " does not exist") <<  endl;
                                        break;
                                    case 6:
                                         cout << "Enter from node: ";
                                         cin >> from;
                                         cout << "Enter to node: ";
                                         cin >> to;
                                         cout << "Edge from " << from << " to " << to << (graph.containsEdge(from, to) ? " exists" : " does not exist") <<  endl;
                                        break;
                                    case 7:
                                         cout << "Node count: " << graph.getNodeCount() <<  endl;
                                        break;
                                    case 8:
                                         cout << "Edge count: " << graph.getEdgeCount() <<  endl;
                                        break;
                                    case 9:
                                         cout << "Enter node value: ";
                                         cin >> value;
                                         cout << "Degree of node " << value << ": " << graph.getNodeDegree(value) <<  endl;
                                        break;
                                    case 10:
                                         cout << "Graph structure:\n";
                                         cout << graph;
                                        break;
                                    case 11:
                                         cout << "Nodes:\n";
                                        for (auto it = graph.begin(); it != graph.end(); ++it) {
                                             cout << it->value << " ";
                                        }
                                         cout <<  endl;
                                        break;
                                    case 12:
                                         cout << "Edges:\n";
                                        for (auto it = graph.edges_begin(); it != graph.edges_end(); ++it) {
                                             cout << "(" << it->first << ", " << it->second << ") ";
                                        }
                                         cout <<  endl;
                                        break;
                                    case 13:
                                         cout << "Enter node value to remove by iterator: ";
                                         cin >> value;
                                        for (auto it = graph.begin(); it != graph.end(); ++it) {
                                            if (it->value == value) {
                                                graph.removeNode(it);
                                                break;
                                            }
                                        }
                                        break;
                                    case 14:
                                         cout << "Enter from node: ";
                                         cin >> from;
                                         cout << "Enter to node: ";
                                         cin >> to;
                                        for (auto it = graph.edges_begin(); it != graph.edges_end(); ++it) {
                                            if (it->first == from && it->second == to) {
                                                graph.removeEdge(it);
                                                break;
                                            }
                                        }
                                        break;
                                    case 15:
                                         cout << "Enter node value to iterate over adjacent nodes: ";
                                         cin >> value;
                                        if (graph.containsNode(value)) {
                                            Node* node = graph.findNode(value);
                                             cout << "Adjacent nodes to " << value << ": ";
                                            for (auto adjIt = graph.adjacent_nodes_begin(*node); adjIt != graph.adjacent_nodes_end(); ++adjIt) {
                                                 cout << adjIt->value << " ";
                                            }
                                             cout <<  endl;
                                        }
                                        else {
                                             cout << "Node " << value << " does not exist." <<  endl;
                                        }
                                        break;
                                    case 0:
                                         cout << "Exiting...\n";
                                        break;
                                    default:
                                         cout << "Invalid choice. Please try again.\n";
                                    }
                                }
                                catch (const  exception& e) {
                                     cerr << "Exception: " << e.what() <<  endl;
                                }
                            } while (choice != 0);

                            return 0;
                        }