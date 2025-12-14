
%﻿ Лабораторная работа №2 по дисциплине "Логические Основы Интеллектуальных Систем"
% Выполнена студентом группы 321701: Политыко Ильей Андреевичем
% Вариант: 10
% 05.06.2025
%
% Задание:
% Решения судоку, можно на меньшем поле(4x4). Задается начальное состояние. Требуется достигнуть целевого.
%
% Использованные источники:
% Справочная система по дисциплине ЛОИС
% Логические основы интеллектуальных систем. Практикум


:- use_module(library(clpfd)).

sudoku4x4(Puzzle) :-
    length(Puzzle, 16),
    
    Puzzle ins 1..4,
    
    Puzzle = [A1,A2,A3,A4,B1,B2,B3,B4,C1,C2,C3,C4,D1,D2,D3,D4],
    
    Rows = [[A1,A2,A3,A4],
            [B1,B2,B3,B4],
            [C1,C2,C3,C4],
            [D1,D2,D3,D4]],
    
    maplist(all_distinct, Rows),     
    transpose(Rows, Cols),
    maplist(all_distinct, Cols),     
    blocks(Rows, Blocks),
    maplist(all_distinct, Blocks),   
    
    label(Puzzle),
    
    print_solution(Rows).

blocks([Row1,Row2,Row3,Row4], Blocks) :-
    Row1 = [A1,A2,A3,A4],
    Row2 = [B1,B2,B3,B4],
    Row3 = [C1,C2,C3,C4],
    Row4 = [D1,D2,D3,D4],
    Blocks = [[A1,A2,B1,B2], [A3,A4,B3,B4],
              [C1,C2,D1,D2], [C3,C4,D3,D4]].

print_solution([R1,R2,R3,R4]) :-
    format('Решение:~n~w~n~w~n~w~n~w~n', [R1,R2,R3,R4]).

% :- example:
%     Puzzle = [4,_,_,_,
%            1,2,_,_,
%            _,_,_,2,
%            2,1,_,_], 
%     sudoku4x4(Puzzle).