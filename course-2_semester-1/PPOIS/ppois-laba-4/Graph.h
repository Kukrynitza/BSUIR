#pragma once
#include <iostream>
#include <vector>
#include <stdexcept>
#include <algorithm>
#include <memory>
#include <sstream>
#include <iterator>
#include <utility>
using namespace std;
// Структура ребра для графа
struct Edge {
    int to;        
    Edge* next;

    Edge(int to, Edge* next = nullptr) : to(to), next(next) {}
};

// Структура узла графа
struct Node {
    int value;         
    Edge* head;       

    Node(int value) : value(value), head(nullptr) {}
};

template <typename T>
class Graph {
public:
    typedef T value_type;
    typedef T& reference;
    typedef const T& const_reference;
    typedef T* pointer;
    typedef const T* const_pointer;

private:
     vector< unique_ptr<Node>> nodes;  // Список узлов графа

public:
    Graph() {}

    // Конструктор копирования
    Graph(const Graph& other) {
        for (const auto& node : other.nodes) {
            addNode(node->value);
        }
        for (const auto& node : other.nodes) {
            Edge* current = node->head;
            while (current) {
                addEdge(node->value, current->to);
                current = current->next;
            }
        }
    }

    // Оператор присваивания
    Graph& operator=(const Graph& other) {
        if (this != &other) {
            clear();
            for (const auto& node : other.nodes) {
                addNode(node->value);
            }
            for (const auto& node : other.nodes) {
                Edge* current = node->head;
                while (current) {
                    addEdge(node->value, current->to);
                    current = current->next;
                }
            }
        }
        return *this;
    }

    // Метод для добавления узла
    void addNode(T value) {
        nodes.push_back( make_unique<Node>(value));
         cout << "Added node: " << value <<  endl; // Отладочное сообщение
    }

    // Метод для добавления ребра (ориентированного)
    void addEdge(T from, T to) {
        Node* fromNode = findNode(from);
        Node* toNode = findNode(to);

        if (!fromNode) {
             ostringstream oss;
            oss << "Source node not found: " << from;
            throw  invalid_argument(oss.str());
        }
        if (!toNode) {
             ostringstream oss;
            oss << "Destination node not found: " << to;
            throw  invalid_argument(oss.str());
        }

        fromNode->head = new Edge(to, fromNode->head);
         cout << "Added edge from " << from << " to " << to <<  endl;
    }

    // Метод для удаления узла
    void removeNode(T value) {
        auto it =  remove_if(nodes.begin(), nodes.end(), [value](const  unique_ptr<Node>& node) {
            return node->value == value;
            });
        if (it == nodes.end()) {
            throw  invalid_argument("Node not found");
        }

        for (auto& node : nodes) {
            removeEdges(node->head, value);
        }

        nodes.erase(it, nodes.end());
    }

    // Метод для удаления ребра
    void removeEdge(T from, T to) {
        Node* fromNode = findNode(from);
        if (!fromNode) {
            throw  invalid_argument("Source node not found");
        }

        removeEdges(fromNode->head, to);
    }

    // Метод для проверки наличия узла
    bool containsNode(T value) const {
        return findNode(value) != nullptr;
    }

    // Метод для проверки наличия ребра
    bool containsEdge(T from, T to) const {
        Node* fromNode = findNode(from);
        if (!fromNode) {
            return false;
        }

        Edge* current = fromNode->head;
        while (current) {
            if (current->to == to) {
                return true;
            }
            current = current->next;
        }
        return false;
    }

    // Метод для получения количества узлов
    size_t getNodeCount() const {
        return nodes.size();
    }

    // Метод для получения количества ребер
    size_t getEdgeCount() const {
        size_t count = 0;
        for (const auto& node : nodes) {
            Edge* current = node->head;
            while (current) {
                count++;
                current = current->next;
            }
        }
        return count;
    }

    // Метод для вычисления степени вершины
    size_t getNodeDegree(T value) const {
        Node* node = findNode(value);
        if (!node) {
            throw  invalid_argument("Node not found");
        }

        size_t degree = 0;
        Edge* current = node->head;
        while (current) {
            degree++;
            current = current->next;
        }
        return degree;
    }

    // Очистка графа
    void clear() {
        for (auto& node : nodes) {
            Edge* current = node->head;
            while (current) {
                Edge* next = current->next;
                delete current;
                current = next;
            }
            node->head = nullptr;
        }
        nodes.clear();
    }

    // Проверка на пустой граф
    bool empty() const {
        return nodes.empty();
    }

    // Печать графа (с использованием итераторов)
    void printGraph() const {
        for (const auto& node : nodes) {
             cout << "Node " << node->value << ":";
            Edge* current = node->head;
            while (current) {
                 cout << " -> " << current->to;
                current = current->next;
            }
             cout <<  endl;
        }
    }

    // Перегрузка оператора вывода
    friend  ostream& operator<<( ostream& os, const Graph& graph) {
        graph.printGraph();
        return os;
    }

    // Операторы сравнения
    bool operator==(const Graph& other) const {
        if (nodes.size() != other.nodes.size()) {
            return false;
        }

        for (const auto& node : nodes) {
            const Node* otherNode = other.findNode(node->value);
            if (!otherNode) {
                return false;
            }

            Edge* current = node->head;
            Edge* otherCurrent = otherNode->head;
            while (current && otherCurrent) {
                if (current->to != otherCurrent->to) {
                    return false;
                }
                current = current->next;
                otherCurrent = otherCurrent->next;
            }

            if (current || otherCurrent) {
                return false;
            }
        }

        return true;
    }

    bool operator!=(const Graph& other) const {
        return !(*this == other);
    }

    // Деструктор
    ~Graph() {
        clear();
    }

    // Итераторы
    class NodeIterator : public  iterator< bidirectional_iterator_tag, Node> {
        typename  vector< unique_ptr<Node>>::iterator it;

    public:
        NodeIterator(typename  vector< unique_ptr<Node>>::iterator it) : it(it) {}

        Node& operator*() const { return **it; }
        Node* operator->() const { return it->get(); }

        NodeIterator& operator++() { ++it; return *this; }
        NodeIterator operator++(int) { NodeIterator tmp = *this; ++it; return tmp; }

        NodeIterator& operator--() { --it; return *this; }
        NodeIterator operator--(int) { NodeIterator tmp = *this; --it; return tmp; }

        bool operator==(const NodeIterator& other) const { return it == other.it; }
        bool operator!=(const NodeIterator& other) const { return it != other.it; }
    };

    class EdgeIterator : public  iterator< bidirectional_iterator_tag,  pair<int, int>> {
        Node* node;
        Edge* edge;

    public:
        EdgeIterator(Node* node, Edge* edge) : node(node), edge(edge) {}

         pair<int, int> operator*() const { return { node->value, edge->to }; }
         pair<int, int>* operator->() const { return new  pair<int, int>(node->value, edge->to); }

        EdgeIterator& operator++() { edge = edge->next; return *this; }
        EdgeIterator operator++(int) { EdgeIterator tmp = *this; edge = edge->next; return tmp; }

        bool operator==(const EdgeIterator& other) const { return edge == other.edge; }
        bool operator!=(const EdgeIterator& other) const { return edge != other.edge; }
    };

    class IncidentEdgeIterator : public  iterator< bidirectional_iterator_tag, Edge> {
        Edge* edge;

    public:
        IncidentEdgeIterator(Edge* edge) : edge(edge) {}

        Edge& operator*() const { return *edge; }
        Edge* operator->() const { return edge; }

        IncidentEdgeIterator& operator++() { edge = edge->next; return *this; }
        IncidentEdgeIterator operator++(int) { IncidentEdgeIterator tmp = *this; edge = edge->next; return tmp; }

        bool operator==(const IncidentEdgeIterator& other) const { return edge == other.edge; }
        bool operator!=(const IncidentEdgeIterator& other) const { return edge != other.edge; }
    };

    class AdjacentNodeIterator : public  iterator< forward_iterator_tag, Node> {
        Edge* edge;
        Graph* graph;

    public:
        AdjacentNodeIterator(Edge* edge, Graph* graph) : edge(edge), graph(graph) {}

        Node& operator*() const { return *graph->findNode(edge->to); }
        Node* operator->() const { return graph->findNode(edge->to); }

        AdjacentNodeIterator& operator++() { edge = edge->next; return *this; }
        AdjacentNodeIterator operator++(int) { AdjacentNodeIterator tmp = *this; edge = edge->next; return tmp; }

        bool operator==(const AdjacentNodeIterator& other) const { return edge == other.edge; }
        bool operator!=(const AdjacentNodeIterator& other) const { return edge != other.edge; }
    };

    NodeIterator begin() { return NodeIterator(nodes.begin()); }
    NodeIterator end() { return NodeIterator(nodes.end()); }

    EdgeIterator edges_begin() {
        for (auto& node : nodes) {
            if (node->head) return EdgeIterator(node.get(), node->head);
        }
        return edges_end();
    }

    EdgeIterator edges_end() { return EdgeIterator(nullptr, nullptr); }

    IncidentEdgeIterator incident_edges_begin(Node& node) { return IncidentEdgeIterator(node.head); }
    IncidentEdgeIterator incident_edges_end() { return IncidentEdgeIterator(nullptr); }

    AdjacentNodeIterator adjacent_nodes_begin(Node& node) { return AdjacentNodeIterator(node.head, this); }
    AdjacentNodeIterator adjacent_nodes_end() { return AdjacentNodeIterator(nullptr, this); }

    void removeNode(NodeIterator it) {
        removeNode(it->value);
    }

    void removeEdge(EdgeIterator it) {
        removeEdge(it->first, it->second);
    }

    NodeIterator rbegin() { return NodeIterator(nodes.rbegin()); }
    NodeIterator rend() { return NodeIterator(nodes.rend()); }

    EdgeIterator redges_begin() {
        for (auto& node : nodes) {
            if (node->head) return EdgeIterator(node.get(), node->head);
        }
        return redges_end();
    }

    EdgeIterator redges_end() { return EdgeIterator(nullptr, nullptr); }

    IncidentEdgeIterator rincident_edges_begin(Node& node) { return IncidentEdgeIterator(node.head); }
    IncidentEdgeIterator rincident_edges_end() { return IncidentEdgeIterator(nullptr); }

    AdjacentNodeIterator radjacent_nodes_begin(Node& node) { return AdjacentNodeIterator(node.head, this); }
    AdjacentNodeIterator radjacent_nodes_end() { return AdjacentNodeIterator(nullptr, this); }

    const NodeIterator cbegin() const { return NodeIterator(nodes.cbegin()); }
    const NodeIterator cend() const { return NodeIterator(nodes.cend()); }

    const EdgeIterator cedges_begin() const {
        for (auto& node : nodes) {
            if (node->head) return EdgeIterator(node.get(), node->head);
        }
        return cedges_end();
    }

    const EdgeIterator cedges_end() const { return EdgeIterator(nullptr, nullptr); }

    const IncidentEdgeIterator cincident_edges_begin(const Node& node) const { return IncidentEdgeIterator(node.head); }
    const IncidentEdgeIterator cincident_edges_end() const { return IncidentEdgeIterator(nullptr); }

    const AdjacentNodeIterator cadjacent_nodes_begin(const Node& node) const { return AdjacentNodeIterator(node.head, this); }
    const AdjacentNodeIterator cadjacent_nodes_end() const { return AdjacentNodeIterator(nullptr, this); }

    // Поиск узла по значению
    Node* findNode(T value) const {
        for (const auto& node : nodes) {
            if (node->value == value) {
                return node.get();
            }
        }
        return nullptr;
    }
private:

    // Удаление ребер, связанных с определенной вершиной
    void removeEdges(Edge*& head, T to) {
        while (head && head->to == to) {
            Edge* temp = head;
            head = head->next;
            delete temp;
        }

        Edge* current = head;
        while (current && current->next) {
            if (current->next->to == to) {
                Edge* temp = current->next;
                current->next = current->next->next;
                delete temp;
            }
            else {
                current = current->next;
            }
        }
    }
};