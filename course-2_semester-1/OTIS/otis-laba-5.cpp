#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <unordered_set>
using namespace std;

class Node {
private:
    vector<string> edges;
    string name;
public:
    Node(string& name) : name(name) {}
    void setName(string name) {
        this->name = name;
    }
    void setEdge(string edge) {
        this->edges.push_back(edge);
    }
    void removeEdge(string& edge) {
        for (auto it = edges.begin(); it != edges.end(); ++it) {
            if (*it == edge) {
                edges.erase(it);
                return;
            }
        }
    }
    string getName(){
        return name;
    }
    vector<string> getEdges(){
        return edges;
    }
};

class Graph {
private:
    vector<Node> nodes;
    string name;
public:
    void setName(string name) {
        this->name = name;
    }
    void createNode(string nodeName) {
        nodes.push_back(Node(nodeName));
    }
    void addOrientedEdge(string from, string to) {
        for (auto& node : nodes) {
            if (node.getName() == from) {
                node.setEdge(to);
            }
        }
    }
    void addUnorientedEdge(string from, string to) {
        for (auto& node : nodes) {
            if (node.getName() == from) {
                node.setEdge(to);
            }
        }
        for (auto& node : nodes) {
            if (node.getName() == to) {
                node.setEdge(from);
            }
        }
    }
    void removeOrientedEdge(string from, string to) {
        for (auto& node : nodes) {
            if (node.getName() == from) {
                node.removeEdge(to);
                break;
            }
        }
    }
    void removeNode(string& nodeName) {
        for (auto it = nodes.begin(); it != nodes.end(); ++it) {
            if (it->getName() == nodeName) {
                nodes.erase(it);
                break;
            }
        }
        for (auto& node : nodes) {
            node.removeEdge(nodeName);
        }
    }
    void removeUnorientedEdge(string from, string to) {
        for (auto& node : nodes) {
            if (node.getName() == from) {
                node.removeEdge(to);
                break;
            }
        }
        for (auto& node : nodes) {
            if (node.getName() == to) {
                node.removeEdge(from);
                break;
            }
        }
    }
    void renameNode(string nodeName, string newNodeName) {
        for (auto& node : nodes) {
            for (auto& edge : node.getEdges()) {
                if (edge == nodeName) {
                    addOrientedEdge(node.getName(), newNodeName);
                    removeOrientedEdge(node.getName(), nodeName);
                }
            }
            if (node.getName() == nodeName) {
                node.setName(newNodeName);
            }
        }
    }
    void printGraph() {
        cout << "Граф \"" << name << "\":" << endl;
        for (auto& node : nodes) {
            cout << "Вершина " << node.getName() << " дуга ведет к : ";
            for (auto& edge : node.getEdges()) {
                cout << edge << " ";
            }
            cout << endl;
        }
    }
    void printGraphInfo(string selectedNode) {
        int edgeCount = 0;

        cout << "Граф \"" << name << "\":\n";
        cout << "Количество вершин: " << nodes.size() << endl;

        for (auto& node : nodes) {
            edgeCount += node.getEdges().size();
        }

        cout << "Количество ориентированных дуг " << edgeCount << endl;

        for (auto& node : nodes) {
            int outDegree = node.getEdges().size();
            int inDegree = 0;
            for (auto& otherNode : nodes) {
                if (&node != &otherNode) {
                    for (auto& edge : otherNode.getEdges()) {
                        if (edge == node.getName()) {
                            inDegree++;
                        }
                    }
                }
            }
            cout << "Вершина " << node.getName() << ": Исходящая степень = " << outDegree
                << ", Входящая степень = " << inDegree << endl;
        }

        if (!selectedNode.empty()) {
            for (auto& node : nodes) {
                if (node.getName() == selectedNode) {
                    int outDegree = node.getEdges().size();
                    int inDegree = 0;
                    for (auto& otherNode : nodes) {
                        for (auto& edge : otherNode.getEdges()) {
                            if (edge == selectedNode) {
                                inDegree++;
                            }
                        }
                    }
                    cout << "Вершина " << node.getName() << ": Исходящая степень = " << outDegree
                        << ", Входящая степень = " << inDegree << endl;
                    break;
                }
            }
        }
    }
    int findNodeIndex(string& nodeName){
        for (size_t i = 0; i < nodes.size(); ++i) {
            if (nodes[i].getName() == nodeName) {
                return i;
            }
        }
        return -1;
    }

    void printAdjacencyMatrix(){
        int n = nodes.size();
        vector<vector<int>> matrix(n, vector<int>(n, 0));

        for (size_t i = 0; i < nodes.size(); ++i) {
            for (auto& edge : nodes[i].getEdges()) {
                int j = findNodeIndex(edge);
                if (j != -1) {
                    matrix[i][j] = 1;
                }
            }
        }

        cout << "Матрица смежности:\n";
        for (auto& row : matrix) {
            for (int val : row) {
                cout << val << " ";
            }
            cout << endl;
        }
    }

    bool isPlanar(){
        int V = nodes.size();
        int E = 0;
        for (auto& node : nodes) {
            E += node.getEdges().size();
        }
        E /= 2;

        if (V >= 3 && E <= 3 * V - 6) {
            cout << "Граф планарный.\n";
            return true;
        }
        cout << "Граф не является планарным.\n";
        return false;
    }

    void makePlanar() {
        while (!isPlanar()) {
            for (auto& node : nodes) {
                if (!node.getEdges().empty()) {
                    node.removeEdge(node.getEdges().back());
                    break;
                }
            }
        }
        cout << "Граф приведён к планарному виду.\n";
    }

    bool hasEulerianCycle(){
        for (auto& node : nodes) {
            if (node.getEdges().size() % 2 != 0) {
                return false;
            }
        }
        return true;
    }

    void findEulerianCycle(){
        if (!hasEulerianCycle()) {
            cout << "Эйлеров цикл не существует, так как степени некоторых вершин нечётные.\n";
            return;
        }
        cout << "Эйлеров цикл существует.\n";
    }
    void findAllPathsDFS(string& start, string& end, vector<string>& path, vector<vector<string>>& allPaths, unordered_set<string>& visited) {
        int startIndex = findNodeIndex(start);

        visited.insert(start);
        path.push_back(start);

        if (start == end) {
            allPaths.push_back(path);
        }
        else {
            for (auto& neighbor : nodes[startIndex].getEdges()) {
                if (visited.find(neighbor) == visited.end()) {
                    findAllPathsDFS(neighbor, end, path, allPaths, visited);
                }
            }
        }

        path.pop_back();
        visited.erase(start);
    }
    void findAllPaths(string& start, string& end) {
        vector<vector<string>> allPaths;
        vector<string> path;
        unordered_set<string> visited;
        findAllPathsDFS(start, end, path, allPaths, visited);

        cout << "Все пути от " << start << " до " << end << ":\n";
        for (auto& p : allPaths) {
            for (auto& node : p) {
                cout << node << " ";
            }
            cout << endl;
        }
    }

    void findShortestPath(string& start, string& end) {
        int startIndex = findNodeIndex(start);
        int endIndex = findNodeIndex(end);

        vector<string> parent(nodes.size(), "");
        vector<bool> visited(nodes.size(), false);
        queue<string> q;

        q.push(start);
        visited[startIndex] = true;

        while (!q.empty()) {
            string current = q.front();
            q.pop();
            int currentIndex = findNodeIndex(current);

            if (current == end) {
                break;
            }

            for (auto& neighbor : nodes[currentIndex].getEdges()) {
                int neighborIndex = findNodeIndex(neighbor);
                if (!visited[neighborIndex]) {
                    visited[neighborIndex] = true;
                    parent[neighborIndex] = current;
                    q.push(neighbor);
                }
            }
        }
        vector<string> path;
        for (string at = end; !at.empty(); at = parent[findNodeIndex(at)]) {
            path.push_back(at);
            if (at == start) break;
        }

        if (path.back() != start) {
            cout << "Путь от " << start << " до " << end << " не найден." << endl;
            return;
        }

        cout << "Кратчайший путь от " << start << " до " << end << ": ";
        for (auto it = path.rbegin(); it != path.rend(); ++it) {
            cout << *it;
            if (it + 1 != path.rend()) cout << " -> ";
        }
        cout << endl;
    }
    int findDistance(string& start, string& end) {
        if (start == end) return 0;

        int startIndex = findNodeIndex(start);
        int endIndex = findNodeIndex(end);

        if (startIndex == -1 || endIndex == -1) {
            cout << "Один или оба узла не найдены в графе.\n";
            return -1;
        }

        vector<bool> visited(nodes.size(), false);
        queue<pair<string, int>> q;
        q.push({ start, 0 });
        visited[startIndex] = true;

        while (!q.empty()) {
            pair<string, int> currentPair = q.front();
            string current = currentPair.first;
            int distance = currentPair.second;
            q.pop();
            int currentIndex = findNodeIndex(current);

            for (auto& neighbor : nodes[currentIndex].getEdges()) {
                if (neighbor == end) {
                    return distance + 1;
                }

                int neighborIndex = findNodeIndex(neighbor);
                if (!visited[neighborIndex]) {
                    visited[neighborIndex] = true;
                    q.push({ neighbor, distance + 1 });
                }
            }
        }

        cout << "Путь от " << start << " до " << end << " не найден.\n";
        return -1;
    }
};

int main() {
    system("chcp 1251");
    Graph graph;
    graph.setName("Торпеда");

    int choice;
    string nodeName, from, to, newNodeName;

    do {
        cout << "\n--- Меню ---\n";
        cout << "1. Создать узел\n";
        cout << "2. Добавить ориенторованную дугу\n";
        cout << "3. Добавить неориенторованную дугу\n";
        cout << "4. Удалить ориенторованную дугу\n";
        cout << "5. Удалить неориенторованную дугу\n";
        cout << "6. Удалить узел\n";
        cout << "7. Переименовать узел\n";
        cout << "8. Вывести граф\n";
        cout << "9. Вывести информацию о графе\n";
        cout << "10. Назвать граф\n";
        cout << "11. Вывести матрицу смежности\n";
        cout << "12. Проверить граф на планарность\n";
        cout << "13. Сделать граф планарным\n";
        cout << "14. Проверить граф на наличае Эйлеровых циклов\n";
        cout << "15. Поиск кратчайшего пути от вершины к вершине\n";
        cout << "16. Поиск всех путей от вершины к вершине\n";
        cout << "17. Расстояние между вершинами\n";
        cout << "0. Выход\n";
        cout << "Ввод: ";
        cin >> choice;

        switch (choice) {
        case 1:
            cout << "Введите название узла: ";
            cin >> nodeName;
            graph.createNode(nodeName);
            break;

        case 2:
            cout << "Введите название узла отправления: ";
            cin >> from;
            cout << "Введите название узла прибытия: ";
            cin >> to;
            graph.addOrientedEdge(from, to);
            break;

        case 3:
            cout << "Введите название узла отправления: ";
            cin >> from;
            cout << "Введите название узла прибытия: ";
            cin >> to;
            graph.addUnorientedEdge(from, to);
            break;

        case 4:
            cout << "Введите название узла отправления: ";
            cin >> from;
            cout << "Введите название узла прибытия: ";
            cin >> to;
            graph.removeOrientedEdge(from, to);
            break;

        case 5:
            cout << "Введите название узла отправления:";
            cin >> from;
            cout << "Введите название узла прибытия: ";
            cin >> to;
            graph.removeUnorientedEdge(from, to);
            break;

        case 6:
            cout << "Введите название узла: ";
            cin >> nodeName;
            graph.removeNode(nodeName);
            break;

        case 7:
            cout << "Введите старое название узла: ";
            cin >> nodeName;
            cout << "Введите новое название узла: ";
            cin >> newNodeName;
            graph.renameNode(nodeName, newNodeName);
            break;

        case 8:
            graph.printGraph();
            break;

        case 9:
            cout << "Введите название узла: ";
            cin >> nodeName;
            graph.printGraphInfo(nodeName);
            break;
        case 10:
            cout << "Введите название графа: ";
            cin >> nodeName;
            graph.setName(nodeName);
            break;
        case 11:
            graph.printAdjacencyMatrix();
            break;
        case 12:
            graph.isPlanar();
            break;
        case 13:
            graph.makePlanar();
            break;
        case 14:
            if (graph.hasEulerianCycle()) {
                graph.findEulerianCycle();
            }
            else {
                cout << "Эйлеров цикл не найден.\n";
            }
            break;
        case 15:
            cout << "Введите название выршины отправления:";
            cin >> from;
            cout << "Введите название вершины прибытия: ";
            cin >> to;
            graph.findShortestPath(from, to);
            break;
        case 16:
            cout << "Введите название выршины отправления:";
            cin >> from;
            cout << "Введите название вершины прибытия: ";
            cin >> to;
            graph.findAllPaths(from, to);
            break;
        case 17:
        cout << "Введите название выршины отправления:";
        cin >> from;
        cout << "Введите название вершины прибытия: ";
        cin >> to;
        int distance;
        distance = graph.findDistance(from, to);
        if (distance != -1) {
            cout << distance << " ребра\n";
        }
        else {
            cout << "Путь не найден.\n";
        }
            break;
        case 0:
            cout << "Выход\n";
            break;

        default:
            cout << "Неправильнный ввод. Повторите\n";
            break;
        }
    } while (choice != 0);
    //graph.setName("Граф Вурдаласку");

    //graph.createNode("A");
    //graph.createNode("B");
    //graph.createNode("C");
    //graph.createNode("D");

    //graph.addOrientedEdge("A", "B");
    //graph.addOrientedEdge("A", "C");
    //graph.addOrientedEdge("B", "D");
    //graph.addUnorientedEdge("C", "D");

    //graph.printGraph();
    //graph.printGraphInfo("");
    //graph.printGraphInfo("A");
    //graph.printAdjacencyMatrix();

    //graph.isPlanar();
    //graph.makePlanar();
    //if (graph.hasEulerianCycle()) {
    //    graph.findEulerianCycle();
    //}
    //else {
    //    cout << "Эйлеров цикл не найден.\n";
    //}
    //string start = "A", end = "D";
    //cout << "Поиск всех путей от " << start << " до " << end << ":\n";
    //graph.findAllPaths(start, end);

    //cout << "Поиск кратчайшего пути от " << start << " до " << end << ":\n";
    //graph.findShortestPath(start, end);
    //cout << "Расстояние от " << start << " до " << end << ": ";
    //int distance = graph.findDistance(start, end);
    //if (distance != -1) {
    //    cout << distance << " ребра\n";
    //}
    //else {
    //    cout << "Путь не найден.\n";
    //}
    return 0;
}