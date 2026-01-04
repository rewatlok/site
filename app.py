'''
contests_dashboard/
├── app.py
├── contests/
│   ├── contest_0001/
│   │   ├── contest_analysis.pdf
│   │   ├── tags.txt
│   │   ├── div1/
│   │   │   ├── monitor.csv
│   │   │   ├── link.txt
│   │   │   └── change.txt
│   │   ├── div2/
│   │   │   ├── monitor.csv
│   │   │   ├── link.txt
│   │   │   └── change.txt
│   │   ├── div3/
│   │   │   ├── monitor.csv
│   │   │   ├── link.txt
│   │   │   └── change.txt
│   │   └── div4/
│   │       ├── monitor.csv
│   │       ├── link.txt
│   │       └── change.txt
├── trainings/
│   ├── training_0001/
│   │   ├── monitor.csv
│   │   ├── video.txt
│   │   ├── contest_analysis.pdf
│   │   ├── tags.txt
│   │   └── change.txt
├── team_contests/
│   ├── contest_0001/
│   │   ├── monitor.csv
│   │   ├── link.txt
│   │   ├── processed.txt
│   │   ├── contest_analysis.pdf
│   │   └── tags.txt
├── math/
│   ├── 001_combinatorics.pdf
│   ├── 001_combinatorics_solutions.pdf
│   ├── 001_combinatorics.txt
│   ├── 002_geometry.pdf
│   ├── 002_geometry_solutions.pdf
│   └── 002_geometry.txt
├── news/
│   ├── headline_001.txt
│   ├── headline_001.pdf
│   ├── headline_002.txt
│   └── headline_002.pdf
└── contestants/
    └── all_ratings.txt
'''

import itertools
import math
import time

from flask import Flask, render_template_string, send_from_directory, jsonify, request
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib
import json

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import re
import csv

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contests Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }
        body {
            background-color: #f0f0f0;
            color: #333;
        }
        .container {
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: white;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            flex-wrap: wrap;
        }
        .tab {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .tab:hover {
            background: #f0f0f0;
        }
        .tab.active {
            background: #3b5998;
            color: white;
        }
        .main-content {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 20px;
            flex: 1;
        }
        .news-header {
            background: #3b5998;
            color: white;
            padding: 15px 20px;
            font-size: 18px;
            font-weight: bold;
            border-bottom: 2px solid #2d4373;
        }
        .news-container {
            height: 600px;
            overflow-y: auto;
            padding: 0;
        }
        .contest-item {
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.2s;
        }
        .contest-item:hover {
            background-color: #f8f9fa;
        }
        .contest-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        .contest-type {
            background: #4CAF50;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .contest-type.training {
            background: #9C27B0;
        }
        .contest-type.team {
            background: #FF5722;
        }
        .contest-type.news {
            background: #2196F3;
        }
        .contest-type.math {
            background: #673AB7;
        }
        .contest-name {
            font-weight: bold;
            color: #1a73e8;
            font-size: 16px;
        }
        .contest-info {
            color: #666;
            font-size: 14px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        .contest-divisions {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin: 10px 0;
        }
        .division-badge {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
            color: white;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
        }
        .division-badge:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 3px 8px rgba(0,0,0,0.2);
        }
        .division-badge:disabled {
            cursor: not-allowed;
            opacity: 0.7;
        }
        .division-1 { background: #FF0000; color: white; }
        .division-2 { background: #FF9800; color: white; }
        .division-3 { background: #4CAF50; color: white; }
        .division-4 { background: #2196F3; color: white; }
        .contest-stats {
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: #666;
            margin-top: 10px;
        }
        .contest-links {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        .contest-link {
            padding: 5px 15px;
            background: #e8f0fe;
            color: #1a73e8;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
            border: 1px solid #d2e3fc;
            transition: all 0.2s;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .contest-link:hover:not(.disabled) {
            background: #1a73e8;
            color: white;
        }
        .contest-link.disabled {
            background: #f5f5f5;
            color: #bdbdbd;
            border-color: #e0e0e0;
            cursor: not-allowed;
            opacity: 0.6;
        }
        .contest-link.green {
            background: #e8f5e9;
            color: #2e7d32;
            border-color: #c8e6c9;
        }
        .contest-link.green:hover:not(.disabled) {
            background: #2e7d32;
            color: white;
        }
        .contest-link.process {
            background: linear-gradient(135deg, #ff9800, #ff5722);
            color: white;
            border: none;
            font-weight: bold;
        }
        .contest-link.process:hover:not(.disabled) {
            background: linear-gradient(135deg, #f57c00, #e64a19);
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(255, 87, 34, 0.3);
        }

        .sidebar-container {
            width: 400px;
            display: flex;
            flex-direction: column;
            gap: 20px; /* Это создаст отступ 20px между секциями */
            align-self: flex-start;
        }

        .sidebar-section {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .rating-section {
            flex: 1;
        }

        .upcoming-section {
            margin-top: 0;
        }

        .rating-header {
            background: #ff6b35;
            color: white;
            padding: 15px 20px;
            font-size: 18px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .show-all {
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 5px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        .show-all:hover {
            background: rgba(255,255,255,0.3);
        }
        .rating-container {
            padding: 10px 0;
            max-height: 350px;
            overflow-y: auto;
        }
        .rating-item {
            display: flex;
            align-items: center;
            padding: 8px 20px;
            border-bottom: 1px solid #f0f0f0;
            cursor: pointer;
            transition: all 0.2s;
        }
        .rating-item:hover {
            background: #f8f9fa;
        }
        .rating-rank {
            width: 35px;
            text-align: center;
            font-weight: bold;
            color: #666;
            font-size: 16px;
        }
        .rating-avatar {
            width: 36px; /* Уменьшить с 40px */
            height: 36px; /* Уменьшить с 40px */
            margin: 0 12px; /* Уменьшить с 15px */
            font-size: 16px; /* Уменьшить с 18px */
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .rating-info {
            flex: 1;
        }
        .rating-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 3px;
        }
        .rating-details {
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: #666;
        }
        .rating-score {
            color: #ff6b35;
            font-weight: bold;
            font-size: 16px;
            margin-left: 10px;
        }
        .rating-tasks-score {
            color: #4CAF50;
            font-weight: bold;
            font-size: 14px;
            margin-left: 5px;
        }
        .rating-graph-btn {
            background: none;
            border: 1px solid #ddd;
            color: #666;
            padding: 3px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
            transition: all 0.2s;
        }
        .rating-graph-btn:hover {
            background: #f0f0f0;
        }

        .upcoming-header {
            background: #3b5998;
            color: white;
            padding: 15px 20px;
            font-size: 18px;
            font-weight: bold;
            border-bottom: 2px solid #2d4373;
        }

        .upcoming-content {
            padding: 0;
            max-height: 300px;
            overflow-y: auto;
        }

        .upcoming-list {
            padding: 15px;
        }

        .upcoming-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #3b5998;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 8px;
            border: 1px solid #e0e0e0;
        }
        .upcoming-item:hover {
            background: #f0f7ff;
            transform: translateX(2px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .upcoming-name {
            font-weight: 600;
            color: #333;
            font-size: 14px;
        }
        .upcoming-date {
            color: #666;
            font-size: 12px;
            margin-top: 3px;
        }
        .upcoming-divisions {
            display: flex;
            gap: 3px;
        }
        .upcoming-division {
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
            color: white;
        }

        .search-box {
            background: white;
            margin-bottom: 20px;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .search-input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            transition: border 0.2s;
            margin-bottom: 10px;
        }
        .search-input:focus {
            outline: none;
            border-color: #1a73e8;
        }

        /* Стили для улучшенного выбора тегов */
        .tag-filter-container {
            position: relative;
            margin-bottom: 10px;
        }

        .tag-filter-toggle {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            color: #666;
            transition: all 0.2s;
        }

        .tag-filter-toggle:hover {
            border-color: #1a73e8;
            background: #f8f9fa;
        }

        .tag-filter-toggle.active {
            border-color: #1a73e8;
            background: #e8f0fe;
        }

        .tag-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 6px;
            margin-top: 5px;
            padding: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            z-index: 1000;
            max-height: 400px;
            overflow-y: auto;
            display: none;
        }

        .tag-dropdown.active {
            display: block;
        }

        .tag-categories {
            margin-bottom: 15px;
        }

        .tag-category {
            margin-bottom: 15px;
        }

        .category-title {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .tag-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .tag-btn {
            padding: 6px 12px;
            background: #e8f0fe;
            color: #1a73e8;
            border: 1px solid #d2e3fc;
            border-radius: 15px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            white-space: nowrap;
        }

        .tag-btn:hover {
            background: #1a73e8;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(26, 115, 232, 0.3);
        }

        .tag-btn.active {
            background: #1a73e8;
            color: white;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(26, 115, 232, 0.3);
        }

        .tag-btn.contest {
            background: #e8f5e9;
            color: #2e7d32;
            border-color: #c8e6c9;
        }

        .tag-btn.contest:hover {
            background: #2e7d32;
            color: white;
        }

        .tag-btn.contest.active {
            background: #2e7d32;
            color: white;
        }

        .tag-btn.training {
            background: #f3e5f5;
            color: #7b1fa2;
            border-color: #e1bee7;
        }

        .tag-btn.training:hover {
            background: #7b1fa2;
            color: white;
        }

        .tag-btn.training.active {
            background: #7b1fa2;
            color: white;
        }

        .tag-btn.team {
            background: #ffecb3;
            color: #ff6f00;
            border-color: #ffd180;
        }

        .tag-btn.team:hover {
            background: #ff6f00;
            color: white;
        }

        .tag-btn.team.active {
            background: #ff6f00;
            color: white;
        }

        .tag-btn.math {
            background: #e8eaf6;
            color: #303f9f;
            border-color: #c5cae9;
        }

        .tag-btn.math:hover {
            background: #303f9f;
            color: white;
        }

        .tag-btn.math.active {
            background: #303f9f;
            color: white;
        }

        .tag-btn.news {
            background: #e3f2fd;
            color: #1565c0;
            border-color: #bbdefb;
        }

        .tag-btn.news:hover {
            background: #1565c0;
            color: white;
        }

        .tag-btn.news.active {
            background: #1565c0;
            color: white;
        }

        .tag-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }

        .selected-tags-container {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            display: none;
        }

        .selected-tags-container.has-tags {
            display: block;
        }

        .selected-tags-header {
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .selected-tags-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .selected-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: white;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 500;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }

        .selected-tag .remove-tag {
            cursor: pointer;
            font-size: 14px;
            opacity: 0.7;
            width: 16px;
            height: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.2s;
        }

        .selected-tag .remove-tag:hover {
            opacity: 1;
            background: rgba(0,0,0,0.1);
        }

        .clear-all-tags {
            background: none;
            border: none;
            color: #f44336;
            cursor: pointer;
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .clear-all-tags:hover {
            background: rgba(244, 67, 54, 0.1);
        }

        .no-upcoming-contests {
            text-align: center;
            padding: 30px 20px;
            color: #999;
            font-size: 14px;
        }

        .no-upcoming-contests i {
            font-size: 36px;
            margin-bottom: 10px;
            opacity: 0.5;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 2% auto;
            padding: 15px;
            border-radius: 10px;
            width: 95%;
            max-width: 1200px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 5px 30px rgba(0,0,0,0.3);
        }
        .close-modal {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close-modal:hover {
            color: #000;
        }
        .chart-container {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
        }
        .chart-img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 12px;
        }
        .results-table th {
            background: #f0f0f0;
            padding: 8px 4px;
            text-align: center;
            border: 1px solid #ddd;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            position: relative;
        }
        .results-table td {
            padding: 8px 4px;
            border: 1px solid #ddd;
            text-align: center;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .results-table tr:nth-child(even) {
            background: #f9f9f9;
        }
        .results-table tr:hover {
            background: #f0f7ff;
        }
        .results-table th.fixed-left,
        .results-table td.fixed-left {
            position: sticky;
            left: 0;
            background: white;
            z-index: 10;
            border-right: 2px solid #ddd;
            width: 50px;
            min-width: 50px;
            max-width: 50px;
            text-align: center;
            font-weight: bold;
        }
        .results-table th.fixed-left-2,
        .results-table td.fixed-left-2 {
            position: sticky;
            left: 50px;
            background: white;
            z-index: 10;
            border-right: 2px solid #ddd;
            width: 180px;
            min-width: 180px;
            max-width: 180px;
            text-align: left;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .results-table tr:nth-child(even) .fixed-left,
        .results-table tr:nth-child(even) .fixed-left-2 {
            background: #f9f9f9;
        }
        .results-table tr:hover .fixed-left,
        .results-table tr:hover .fixed-left-2 {
            background: #f0f7ff;
        }
        .results-table th.fixed-left,
        .results-table th.fixed-left-2 {
            position: sticky;
            top: 0;
            background: #f0f0f0 !important;
            z-index: 20;
            border-bottom: 2px solid #ddd;
        }
        .task-header {
            background: #f8f9fa;
            padding: 8px 2px !important;
            text-align: center !important;
            font-weight: bold;
            border: 1px solid #ddd;
            width: 45px !important;
            min-width: 45px !important;
            max-width: 45px !important;
            font-size: 11px;
        }
        .task-cell {
            text-align: center !important;
            padding: 8px 2px !important;
            border: 1px solid #ddd;
            width: 45px !important;
            min-width: 45px !important;
            max-width: 45px !important;
            font-weight: bold;
            font-size: 11px;
        }
        .task-cell.solved {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .task-cell.attempted {
            background: #ffebee;
            color: #c62828;
        }
        .task-cell.pending {
            background: #fff3e0;
            color: #ef6c00;
        }
        .results-table th:nth-child(3),
        .results-table td:nth-child(3),
        .results-table th:nth-child(4),
        .results-table td:nth-child(4),
        .results-table th:nth-child(5),
        .results-table td:nth-child(5),
        .results-table th:nth-child(6),
        .results-table td:nth-child(6) {
            width: 75px;
            min-width: 75px;
            max-width: 75px;
            text-align: center;
        }
        .monitor-container {
            max-height: 70vh;
            overflow: auto;
            margin: 15px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            position: relative;
        }
        .monitor-container table {
            margin: 0;
            min-width: fit-content;
        }
        .contact-info {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-size: 14px;
            color: #666;
        }
        .contact-info a {
            color: #1a73e8;
            text-decoration: none;
            margin: 0 10px;
        }
        .contact-info a:hover {
            text-decoration: underline;
        }
        .division-selector {
            display: flex;
            gap: 10px;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .division-tab {
            padding: 5px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
        }
        .division-tab:hover {
            transform: translateY(-2px);
        }
        .division-tab.active {
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .tasks-count {
            display: inline-block;
            padding: 1px 6px;
            background: rgba(255,255,255,0.3);
            color: white;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
            margin-left: 3px;
        }
        .unofficial-badge {
            background: #9C27B0;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            margin-left: 5px;
        }
        .official-badge {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            margin-left: 5px;
            border: 1px solid #c8e6c9;
        }
        .tasks-badge {
            background: #2196F3;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            margin-left: 5px;
        }
        .monitor-tabs {
            display: flex;
            gap: 5px;
            margin: 10px 0;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .monitor-tab {
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
            border: 1px solid #ddd;
        }
        .monitor-tab:hover {
            background: #e0e0e0;
        }
        .monitor-tab.active {
            background: #3b5998;
            color: white;
            border-color: #3b5998;
        }
        .stats-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-box {
            background: white;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #3b5998;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
        }
        .medal-gold { color: #FFD700; font-weight: bold; }
        .medal-silver { color: #C0C0C0; font-weight: bold; }
        .medal-bronze { color: #CD7F32; font-weight: bold; }
        .results-table a {
            color: #1a73e8;
            text-decoration: none;
            display: block;
            width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .results-table a:hover {
            text-decoration: underline;
        }
        .news-content {
            line-height: 1.6;
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .news-content h3 {
            margin-top: 0;
            color: #333;
        }
        .news-content p {
            margin: 10px 0;
        }
        .news-content ul, .news-content ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        .news-content li {
            margin: 5px 0;
        }
        .news-content a {
            color: #1a73e8;
            text-decoration: none;
        }
        .news-content a:hover {
            text-decoration: underline;
        }
        .tags-container {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
            margin: 8px 0;
        }
        .tag {
            background: #E0E0E0;
            color: #333;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }
        .tag.contest { background: #e8f5e9; color: #2e7d32; }
        .tag.training { background: #f3e5f5; color: #7b1fa2; }
        .tag.team { background: #ffecb3; color: #ff6f00; }
        .tag.math { background: #e8eaf6; color: #303f9f; }
        .tag.news { background: #e3f2fd; color: #1565c0; }
        .rank-novice { color: #804000; }
        .rank-student { color: #808080; }
        .rank-practitioner { color: #008000; }
        .rank-specialist { color: #00C0C0; }
        .rank-expert { color: #0000FF; }
        .rank-candidate { color: #AA00AA; }
        .rank-master { color: #C0C000; }
        .rank-grandmaster { color: #FF8000; }
        .rank-legendary { color: #FF0000; }
        .rank-absolute { color: #FF0066; }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        .monitor-container::-webkit-scrollbar {
            height: 8px;
        }
        .monitor-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            margin: 0 5px;
            border-radius: 4px;
        }
        .monitor-container::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 4px;
            min-width: 100px;
        }
        .monitor-container::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }
        .monitor-container {
            scrollbar-width: thin;
            scrollbar-color: #c1c1c1 #f1f1f1;
        }

        @media (max-width: 1400px) {
            .container {
                flex-direction: column;
            }
            .sidebar-container {
                width: 100%;
                flex-direction: row;
                flex-wrap: wrap;
            }
            .sidebar-section {
                flex: 1;
                min-width: 300px;
            }
            .news-container {
                height: 400px;
            }
            .modal-content {
                width: 95%;
                margin: 2% auto;
            }
            .task-header,
            .task-cell {
                width: 40px !important;
                min-width: 40px !important;
                max-width: 40px !important;
                padding: 6px 1px !important;
                font-size: 10px;
            }
            .results-table th.fixed-left,
            .results-table td.fixed-left {
                width: 45px !important;
                min-width: 45px !important;
                max-width: 45px !important;
            }
            .results-table th.fixed-left-2,
            .results-table td.fixed-left-2 {
                left: 45px;
                width: 150px !important;
                min-width: 150px !important;
                max-width: 150px !important;
            }
        }

        @media (max-width: 768px) {
            .sidebar-section {
                min-width: 100%;
            }
            .tabs {
                flex-direction: column;
            }
            .tab {
                text-align: center;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="search-box">
        <input type="text" 
               class="search-input" 
               placeholder="🔍 Поиск контеста, тренировки, пользователя..."
               id="searchInput"
               onkeyup="filterContent()">

        <div class="tag-filter-container">
            <div class="tag-filter-toggle" id="tagFilterToggle" onclick="toggleTagFilter()">
                <span><i class="fas fa-tags"></i> Фильтр по тегам</span>
                <span id="selectedTagsCount" style="display: none; background: #1a73e8; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">0</span>
            </div>

            <div class="tag-dropdown" id="tagDropdown">
                <div class="tag-categories" id="tagCategories">
                    <!-- Категории тегов будут загружены динамически -->
                </div>

                <div class="tag-actions">
                    <button class="contest-link" onclick="applyTagFilter()" style="flex: 1;">
                        <i class="fas fa-check"></i> Применить
                    </button>
                    <button class="contest-link" onclick="clearAllTags()" style="flex: 1; background: #f8f9fa; color: #666; border: 1px solid #ddd;">
                        <i class="fas fa-times"></i> Очистить
                    </button>
                </div>
            </div>
        </div>

        <div class="selected-tags-container" id="selectedTagsContainer">
            <div class="selected-tags-header">
                <span>Выбранные теги:</span>
                <button class="clear-all-tags" onclick="clearAllTags()">
                    <i class="fas fa-trash-alt"></i> Очистить все
                </button>
            </div>
            <div class="selected-tags-list" id="selectedTagsList">
                <!-- Выбранные теги будут отображаться здесь -->
            </div>
        </div>
    </div>

    <div class="tabs">
        <div class="tab active" onclick="showTab('contests')">
            <i class="fas fa-trophy"></i> Контесты
        </div>
        <div class="tab" onclick="showTab('trainings')">
            <i class="fas fa-dumbbell"></i> Тренировки
        </div>
        <div class="tab" onclick="showTab('team')">
            <i class="fas fa-users"></i> Командные
        </div>
        <div class="tab" onclick="showTab('math')">
            <i class="fas fa-square-root-alt"></i> Математика
        </div>
        <div class="tab" onclick="showTab('news')">
            <i class="fas fa-newspaper"></i> Новости
        </div>
    </div>

    <div class="container" style="display: flex; gap: 20px;">
        <div class="main-content">
            <div class="news-header">
                <span id="tabTitle"><i class="fas fa-trophy"></i> Контесты</span>
            </div>

            <div class="news-container" id="contestsContainer">
                {% if contests %}
                    {% for contest in contests %}
                    <div class="contest-item" 
                         data-id="{{ contest.id }}"
                         data-title="{{ contest.title|lower }}"
                         data-status="{{ 'processed' if contest.processed else 'pending' }}"
                         data-type="contest"
                         data-tags="{{ contest.tags|join(',')|lower }}">

                        <div class="contest-header">
                            <span class="contest-type">КОНТЕСТ {{ contest.number }}</span>
                            {% if contest.processed %}
                            <span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                <i class="fas fa-check"></i> Обработан
                            </span>
                            {% else %}
                            <span style="background: #ff9800; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                <i class="fas fa-clock"></i> В ожидании
                            </span>
                            {% endif %}
                        </div>

<div class="contest-info">
    <span><i class="far fa-calendar"></i> {{ contest.date }}</span>
    {% if contest.processed %}
    <span><i class="fas fa-users"></i> {{ contest.total_participants }} участников</span>
    {% endif %}
    <!-- УБРАЛИ ОТОБРАЖЕНИЕ КОЛИЧЕСТВА ЗАДАЧ -->
</div>

                        {% if contest.tags %}
                        <div class="tags-container">
                            {% for tag in contest.tags %}
                            <span class="tag contest">{{ tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if contest.divisions %}
                        <div class="contest-divisions">
                            {% for div in contest.divisions %}
                                {% if div.link %}
                                <a href="{{ div.link }}" target="_blank" class="division-badge division-{{ div.division }}" 
                                   style="opacity: {% if not contest.processed %}0.7{% else %}1{% endif %};"
                                   {% if not contest.processed %}disabled{% endif %}>
                                    Div {{ div.division }}
                                </a>
                                {% else %}
                                <button class="division-badge division-{{ div.division }}" 
                                        style="opacity: {% if not contest.processed %}0.7{% else %}1{% endif %};"
                                        onclick="{% if contest.processed %}viewContestMonitor('{{ contest.id }}', {{ div.division }}){% endif %}"
                                        {% if not contest.processed %}disabled{% endif %}>
                                    Div {{ div.division }}
                                </button>
                                {% endif %}
                            {% endfor %}
                        </div>
                        {% endif %}

                        {% if contest.processed and contest.winner %}
                        <div class="contest-stats">
                            <span><i class="fas fa-crown"></i> Победитель: {{ contest.winner }}</span>
                            {% if contest.max_rating > 0 %}
                            <span><i class="fas fa-star"></i> Макс. рейтинг: {{ contest.max_rating }}</span>
                            {% endif %}
                        </div>
                        {% endif %}

                        <div class="contest-links">
                            {% if contest.analysis %}
                            <a href="/contest/{{ contest.id }}/{{ contest.analysis }}" target="_blank" class="contest-link green">
                                <i class="fas fa-chart-line"></i> Разбор
                            </a>
                            {% endif %}

                            {% if contest.processed %}
                            <button class="contest-link" onclick="viewContestMonitor('{{ contest.id }}')">
                                <i class="fas fa-table"></i> Монитор
                            </button>

                            {% else %}
                            <button class="contest-link process" onclick="processContest('{{ contest.id }}')">
                                <i class="fas fa-cogs"></i> Обработать
                            </button>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                <div class="contest-item" style="text-align: center; padding: 40px 20px; color: #999;">
                    <i class="fas fa-folder-open" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <h3>Контестов пока нет</h3>
                    <p>Добавьте контесты в папку contests/</p>
                </div>
                {% endif %}
            </div>

            <div class="news-container" id="trainingsContainer" style="display: none;">
                {% if trainings %}
                    {% for training in trainings %}
                    <div class="contest-item" 
                         data-id="{{ training.id }}"
                         data-title="{{ training.title|lower }}"
                         data-type="training"
                         data-tags="{{ training.tags|join(',')|lower }}">

                        <div class="contest-header">
                            <span class="contest-type training">ТРЕНИРОВКА {{ training.number }}</span>
                            {% if training.processed %}
                            <span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                <i class="fas fa-check"></i> Обработана
                            </span>
                            {% else %}
                            <span style="background: #ff9800; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                <i class="fas fa-clock"></i> В ожидании
                            </span>
                            {% endif %}
                        </div>

                        <div class="contest-info">
                            <span><i class="far fa-calendar"></i> {{ training.date }}</span>
                            <span><i class="fas fa-tasks"></i> {{ training.tasks_count }} задач</span>
                            {% if training.processed %}
                            <span><i class="fas fa-users"></i> {{ training.participants }} участников</span>
                            {% endif %}
                        </div>

                        {% if training.tags %}
                        <div class="tags-container">
                            {% for tag in training.tags %}
                            <span class="tag training">{{ tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}

                        <div class="contest-links">
                            {% if training.link %}
                            <a href="{{ training.link }}" target="_blank" class="contest-link">
                                <i class="fas fa-external-link-alt"></i> Тренировка
                            </a>
                            {% endif %}

                            {% if training.tasks_link %}
                            <a href="{{ training.tasks_link }}" target="_blank" class="contest-link">
                                <i class="fas fa-file-alt"></i> Условия задач
                            </a>
                            {% endif %}

                            {% if training.analysis %}
                            <a href="/training/{{ training.id }}/{{ training.analysis }}" target="_blank" class="contest-link green">
                                <i class="fas fa-chart-line"></i> Разбор
                            </a>
                            {% endif %}

                            {% if training.video %}
                            <a href="{{ training.video }}" target="_blank" class="contest-link">
                                <i class="fas fa-video"></i> Видео
                            </a>
                            {% endif %}

                            {% if training.processed %}
                            <button class="contest-link" onclick="viewTrainingMonitor('{{ training.id }}')">
                                <i class="fas fa-table"></i> Монитор
                            </button>
                            <button class="contest-link" onclick="viewTrainingDetails('{{ training.id }}')">
                                <i class="fas fa-chart-bar"></i> Статистика
                            </button>
                            {% else %}
                            <button class="contest-link process" onclick="processTraining('{{ training.id }}')">
                                <i class="fas fa-cogs"></i> Обработать
                            </button>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                <div class="contest-item" style="text-align: center; padding: 40px 20px; color: #999;">
                    <i class="fas fa-dumbbell" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <h3>Тренировок пока нет</h3>
                    <p>Добавьте тренировки в папку trainings/</p>
                </div>
                {% endif %}
            </div>

            <div class="news-container" id="teamContainer" style="display: none;">
                {% if team_contests %}
                    {% for contest in team_contests %}
                    <div class="contest-item" 
                         data-id="{{ contest.id }}"
                         data-title="{{ contest.title|lower }}"
                         data-type="team"
                         data-tags="{{ contest.tags|join(',')|lower }}">

                        <div class="contest-header">
                            <span class="contest-type team">КОМАНДНЫЙ {{ contest.number }}</span>
                            {% if contest.processed %}
                            <span style="background: #4CAF50; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                <i class="fas fa-check"></i> Обработан
                            </span>
                            {% else %}
                            <span style="background: #ff9800; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                <i class="fas fa-clock"></i> В ожидании
                            </span>
                            {% endif %}
                        </div>

                        <div class="contest-info">
                            <span><i class="far fa-calendar"></i> {{ contest.date }}</span>
                            <span><i class="fas fa-tasks"></i> {{ contest.tasks_count }} задач</span>
                            {% if contest.processed %}
                            <span><i class="fas fa-users"></i> {{ contest.teams }} команд</span>
                            {% endif %}
                        </div>

                        {% if contest.tags %}
                        <div class="tags-container">
                            {% for tag in contest.tags %}
                            <span class="tag team">{{ tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}

                        <div class="contest-links">
                            {% if contest.link %}
                            <a href="{{ contest.link }}" target="_blank" class="contest-link">
                                <i class="fas fa-external-link-alt"></i> Контест
                            </a>
                            {% endif %}

                            {% if contest.analysis %}
                            <a href="/team_contest/{{ contest.id }}/{{ contest.analysis }}" target="_blank" class="contest-link green">
                                <i class="fas fa-chart-line"></i> Разбор
                            </a>
                            {% endif %}

                            {% if contest.processed %}
                            <button class="contest-link" onclick="viewTeamMonitor('{{ contest.id }}')">
                                <i class="fas fa-table"></i> Монитор
                            </button>
                            {% else %}
                            <button class="contest-link process" onclick="processTeamContest('{{ contest.id }}')">
                                <i class="fas fa-cogs"></i> Обработать
                            </button>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                <div class="contest-item" style="text-align: center; padding: 40px 20px; color: #999;">
                    <i class="fas fa-users" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <h3>Командных контестов пока нет</h3>
                    <p>Добавьте командные контесты в папку team_contests/</p>
                </div>
                {% endif %}
            </div>

            <div class="news-container" id="mathContainer" style="display: none;">
                {% if math_problems %}
                    {% for math in math_problems %}
                    <div class="contest-item" 
                         data-id="{{ math.id }}"
                         data-title="{{ math.title|lower }}"
                         data-type="math"
                         data-tags="{{ math.tags|join(',')|lower }}">

                        <div class="contest-header">
                            <span class="contest-type math">МАТЕМАТИКА {{ math.number }}</span>
                            <span style="background: #673AB7; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                {{ math.date }}
                            </span>
                        </div>

                        <div class="contest-info">
                            <span><i class="fas fa-user"></i> {{ math.author }}</span>
                            <span><i class="fas fa-file-pdf"></i> PDF-документ</span>
                            {% if math.pages %}
                            <span><i class="fas fa-file-alt"></i> {{ math.pages }} страниц</span>
                            {% endif %}
                        </div>

                        <h3 style="margin: 10px 0; color: #333;">{{ math.title }}</h3>

                        {% if math.tags %}
                        <div class="tags-container">
                            {% for tag in math.tags %}
                            <span class="tag math">{{ tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}

                        <div class="contest-links">
                            <a href="/math/{{ math.id }}/{{ math.filename }}" target="_blank" class="contest-link">
                                <i class="fas fa-external-link-alt"></i> Открыть PDF
                            </a>

                            {% if math.solutions_filename %}
                            <a href="/math/{{ math.id }}/{{ math.solutions_filename }}" target="_blank" class="contest-link green">
                                <i class="fas fa-chart-line"></i> Решения
                            </a>
                            {% endif %}

                            <button class="contest-link" onclick="viewMathDetails('{{ math.id }}')">
                                <i class="fas fa-info-circle"></i> Подробнее
                            </button>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                <div class="contest-item" style="text-align: center; padding: 40px 20px; color: #999;">
                    <i class="fas fa-square-root-alt" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <h3>Математических материалов пока нет</h3>
                    <p>Добавьте PDF-файлы с условиями в папку math/</p>
                </div>
                {% endif %}
            </div>

            <div class="news-container" id="newsContainer" style="display: none;">
                {% if news %}
                    {% for item in news %}
                    <div class="contest-item" 
                         data-id="{{ item.id }}"
                         data-title="{{ item.title|lower }}"
                         data-type="news"
                         data-tags="{{ item.tags|join(',')|lower }}">

                        <div class="contest-header">
                            <span class="contest-type news">НОВОСТЬ {{ item.number }}</span>
                            <span style="background: #2196F3; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                {{ item.date }}
                            </span>
                        </div>

                        <div class="contest-info">
                            <span><i class="fas fa-user"></i> {{ item.author }}</span>
                            {% if item.priority == 'high' %}
                            <span style="color: #f44336; font-weight: bold;">
                                <i class="fas fa-exclamation-triangle"></i> Важно!
                            </span>
                            {% elif item.priority == 'medium' %}
                            <span style="color: #ff9800;">
                                <i class="fas fa-info-circle"></i> Информация
                            </span>
                            {% endif %}
                        </div>

                        <h3 style="margin: 10px 0; color: #333;">{{ item.title }}</h3>

                        {% if item.tags %}
                        <div class="tags-container">
                            {% for tag in item.tags %}
                            <span class="tag news">{{ tag }}</span>
                            {% endfor %}
                        </div>
                        {% endif %}

                        <div class="contest-links">
                            <button class="contest-link" onclick="viewNews('{{ item.id }}')">
                                <i class="fas fa-eye"></i> Читать новость
                            </button>
                            {% if item.attachments %}
                            <button class="contest-link" onclick="viewNewsAttachments('{{ item.id }}')">
                                <i class="fas fa-paperclip"></i> Вложения ({{ item.attachments_count }})
                            </button>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                <div class="contest-item" style="text-align: center; padding: 40px 20px; color: #999;">
                    <i class="fas fa-newspaper" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <h3>Новостей пока нет</h3>
                    <p>Добавьте новости в папку news/</p>
                </div>
                {% endif %}
            </div>

            <div class="contact-info">
                <p>Контакты для связи:</p>
                <p>
                    <i class="fab fa-telegram"></i> 
                    <a href="https://t.me/watlok" target="_blank">@watlok</a> • 
                    <i class="fas fa-envelope"></i> 
                    <a href="mailto:rewatlok@gmail.com">rewatlok@gmail.com</a>
                </p>
            </div>
        </div>

        <!-- Разделенная боковая панель -->
        <div class="sidebar-container">
            <!-- Секция рейтинга -->
            <div class="sidebar-section rating-section">
                <div class="rating-header">
                    <span><i class="fas fa-trophy"></i> Рейтинг участников</span>
                    <button class="show-all" onclick="showAllUsers()">Все {{ total_participants }} →</button>
                </div>

                <div class="rating-container">
                    {% if participants %}
                        {% for participant in participants[:15] %}
                        <div class="rating-item" 
                             data-user="{{ participant.nickname|lower }}"
                             data-contests="{{ participant.contests }}"
                             data-rating="{{ participant.rating }}"
                             onclick="showUserGraph('{{ participant.nickname }}')">

                            <div class="rating-rank">
                                {{ loop.index }}
                            </div>

                            <div class="rating-avatar" style="background: {{ participant.avatar_color }};">
                                {{ participant.avatar_text }}
                            </div>

                            <div class="rating-info">
                                <div class="rating-name">
                                    {{ participant.nickname }}
                                    <span class="rating-score" style="color: {{ participant.rank_color }};">
                                        {{ participant.rating }}
                                    </span>
                                    {% if participant.tasks_score > 0 %}
                                    <span class="rating-tasks-score" title="Рейтинг решенных задач">
                                        <i class="fas fa-tasks"></i> {{ participant.tasks_score }}
                                    </span>
                                    {% endif %}
                                </div>
                                <div class="rating-details">
                                    <span><i class="fas fa-flag"></i> {{ participant.contests }} конт.</span>
                                    <span style="color: {{ participant.rank_color }};">
                                        <i class="fas fa-medal"></i> {{ participant.rank }}
                                    </span>
                                </div>
                            </div>

                            <button class="rating-graph-btn" onclick="showUserGraph('{{ participant.nickname }}'); event.stopPropagation();">
                                <i class="fas fa-chart-line"></i>
                            </button>
                        </div>
                        {% endfor %}
                    {% else %}
                    <div class="rating-item" style="text-align: center; padding: 40px 20px; color: #999;">
                        <i class="fas fa-users" style="font-size: 48px; margin-bottom: 15px;"></i>
                        <h3>Нет данных об участниках</h3>
                        <p>Обработайте контесты для расчета рейтингов</p>
                    </div>
                    {% endif %}
                </div>
            </div>

<!-- Секция ближайших контестов -->
<div class="sidebar-section upcoming-section">
    <div class="upcoming-header">
        <i class="fas fa-calendar-alt"></i> Ближайшие контесты
    </div>
    <div class="upcoming-content">
        <div class="upcoming-list">
            {% if upcoming_contests %}
                {% for contest in upcoming_contests %}
                <div class="upcoming-item">
                    <div style="width: 100%;">
                        <div class="upcoming-name">
                            <i class="fas fa-trophy" style="color: #4CAF50; margin-right: 5px;"></i>
                            Контест {{ contest.number }}
                        </div>
                        <div class="upcoming-date" style="margin-bottom: 8px;">
                            <i class="far fa-calendar" style="margin-right: 3px;"></i>
                            {{ contest.date }}
                        </div>
                        {% if contest.divisions %}
                        <div class="contest-divisions" style="gap: 5px; flex-wrap: wrap;">
                            {% for div in contest.divisions %}
                                {% if div.link %}
                                <a href="{{ div.link }}" 
                                   target="_blank" 
                                   class="division-badge division-{{ div.division }}" 
                                   style="padding: 4px 10px; font-size: 11px; text-decoration: none; opacity: 0.9; font-weight: bold;"
                                   onclick="event.stopPropagation();"
                                   title="Div {{ div.division }}">
                                    Div{{ div.division }}
                                </a>
                                {% else %}
                                <button class="division-badge division-{{ div.division }}" 
                                        style="padding: 4px 10px; font-size: 11px; opacity: 0.9; font-weight: bold; border: none; cursor: pointer;"
                                        onclick="event.stopPropagation(); viewContestDetails('{{ contest.id }}', {{ div.division }})"
                                        title="Посмотреть Div {{ div.division }}">
                                    Div{{ div.division }}
                                </button>
                                {% endif %}
                            {% endfor %}
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            {% else %}
            <div class="no-upcoming-contests">
                <i class="far fa-calendar-times"></i>
                <p>Нет предстоящих контестов</p>
                <p style="font-size: 11px; margin-top: 5px;">
                    Все контесты обработаны или нет запланированных
                </p>
            </div>
            {% endif %}
        </div>
    </div>
</div>

        </div>
    </div>

    <!-- Модальные окна -->
    <div id="chartModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal('chartModal')">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>

    <div id="contestModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal('contestModal')">&times;</span>
            <div id="contestModalContent"></div>
        </div>
    </div>

    <div id="trainingModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal('trainingModal')">&times;</span>
            <div id="trainingModalContent"></div>
        </div>
    </div>

    <div id="teamModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal('teamModal')">&times;</span>
            <div id="teamModalContent"></div>
        </div>
    </div>

    <div id="mathModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal('mathModal')">&times;</span>
            <div id="mathModalContent"></div>
        </div>
    </div>

    <div id="monitorModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal('monitorModal')">&times;</span>
            <div id="monitorModalContent"></div>
        </div>
    </div>

    <div id="newsModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal('newsModal')">&times;</span>
            <div id="newsModalContent"></div>
        </div>
    </div>

    <script>
        let currentTab = 'contests';
        let selectedTags = new Set();
        let allTagsByCategory = {};

        function showTab(tab) {
            currentTab = tab;

            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => {
                if (t.textContent.includes(getTabText(tab))) {
                    t.classList.add('active');
                }
            });

            const tabTitle = document.getElementById('tabTitle');
            const containers = ['contestsContainer', 'trainingsContainer', 'teamContainer', 'mathContainer', 'newsContainer'];

            containers.forEach(container => {
                document.getElementById(container).style.display = 'none';
            });

            switch(tab) {
                case 'contests':
                    tabTitle.innerHTML = '<i class="fas fa-trophy"></i> Контесты';
                    document.getElementById('contestsContainer').style.display = 'block';
                    break;
                case 'trainings':
                    tabTitle.innerHTML = '<i class="fas fa-dumbbell"></i> Тренировки';
                    document.getElementById('trainingsContainer').style.display = 'block';
                    break;
                case 'team':
                    tabTitle.innerHTML = '<i class="fas fa-users"></i> Командные контесты';
                    document.getElementById('teamContainer').style.display = 'block';
                    break;
                case 'math':
                    tabTitle.innerHTML = '<i class="fas fa-square-root-alt"></i> Математика';
                    document.getElementById('mathContainer').style.display = 'block';
                    break;
                case 'news':
                    tabTitle.innerHTML = '<i class="fas fa-newspaper"></i> Новости';
                    document.getElementById('newsContainer').style.display = 'block';
                    break;
            }

            filterContent();
        }

        function getTabText(tab) {
            switch(tab) {
                case 'contests': return 'Контесты';
                case 'trainings': return 'Тренировки';
                case 'team': return 'Командные';
                case 'math': return 'Математика';
                case 'news': return 'Новости';
                default: return 'Контесты';
            }
        }

        function loadAllTags() {
            allTagsByCategory = {
                'contest': new Set(),
                'training': new Set(),
                'team': new Set(),
                'math': new Set(),
                'news': new Set()
            };

            // Собираем теги из всех контейнеров
            const containers = {
                'contest': '#contestsContainer .contest-item',
                'training': '#trainingsContainer .contest-item',
                'team': '#teamContainer .contest-item',
                'math': '#mathContainer .contest-item',
                'news': '#newsContainer .contest-item'
            };

            for (const [type, selector] of Object.entries(containers)) {
                const items = document.querySelectorAll(selector);
                items.forEach(item => {
                    const tags = item.dataset.tags ? item.dataset.tags.split(',') : [];
                    tags.forEach(tag => {
                        if (tag.trim()) {
                            allTagsByCategory[type].add(tag.trim());
                        }
                    });
                });
            }

            // Отображаем теги по категориям
            renderTagCategories();
        }

        function renderTagCategories() {
            const tagCategoriesContainer = document.getElementById('tagCategories');
            tagCategoriesContainer.innerHTML = '';

            for (const [category, tagsSet] of Object.entries(allTagsByCategory)) {
                if (tagsSet.size === 0) continue;

                const tags = Array.from(tagsSet).sort();
                const categoryName = getCategoryName(category);

                const categoryHTML = `
                    <div class="tag-category">
                        <div class="category-title">${categoryName}</div>
                        <div class="tag-buttons">
                            ${tags.map(tag => `
                                <button class="tag-btn ${category} ${selectedTags.has(tag) ? 'active' : ''}" 
                                        onclick="toggleTag('${tag.replace(/'/g, "\\'")}', '${category}')">
                                    <i class="fas fa-${getCategoryIcon(category)}"></i>
                                    ${tag}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                `;

                tagCategoriesContainer.innerHTML += categoryHTML;
            }
        }

        function getCategoryName(category) {
            switch(category) {
                case 'contest': return 'Контесты';
                case 'training': return 'Тренировки';
                case 'team': return 'Командные';
                case 'math': return 'Математика';
                case 'news': return 'Новости';
                default: return category;
            }
        }

        function getCategoryIcon(category) {
            switch(category) {
                case 'contest': return 'trophy';
                case 'training': return 'dumbbell';
                case 'team': return 'users';
                case 'math': return 'square-root-alt';
                case 'news': return 'newspaper';
                default: return 'tag';
            }
        }

        function toggleTagFilter() {
            const dropdown = document.getElementById('tagDropdown');
            const toggle = document.getElementById('tagFilterToggle');

            if (dropdown.classList.contains('active')) {
                dropdown.classList.remove('active');
                toggle.classList.remove('active');
            } else {
                dropdown.classList.add('active');
                toggle.classList.add('active');
                loadAllTags();
            }
        }

        function toggleTag(tag, category) {
            if (selectedTags.has(tag)) {
                selectedTags.delete(tag);
            } else {
                selectedTags.add(tag);
            }

            updateSelectedTagsDisplay();
            updateTagButtons();
        }

        function applyTagFilter() {
            toggleTagFilter();
            filterContent();
        }

        function clearAllTags() {
            selectedTags.clear();
            updateSelectedTagsDisplay();
            updateTagButtons();
            filterContent();

            // Скрываем контейнер с выбранными тегами
            const container = document.getElementById('selectedTagsContainer');
            container.classList.remove('has-tags');

            // Обновляем счетчик
            updateSelectedTagsCount();
        }

        function updateSelectedTagsDisplay() {
            const container = document.getElementById('selectedTagsContainer');
            const list = document.getElementById('selectedTagsList');

            if (selectedTags.size === 0) {
                container.classList.remove('has-tags');
                list.innerHTML = '';
            } else {
                container.classList.add('has-tags');

                let html = '';
                selectedTags.forEach(tag => {
                    // Определяем категорию тега
                    let category = 'default';
                    for (const [cat, tagsSet] of Object.entries(allTagsByCategory)) {
                        if (tagsSet.has(tag)) {
                            category = cat;
                            break;
                        }
                    }

                    html += `
                        <div class="selected-tag">
                            <i class="fas fa-${getCategoryIcon(category)}"></i>
                            ${tag}
                            <span class="remove-tag" onclick="removeSelectedTag('${tag.replace(/'/g, "\\'")}')">×</span>
                        </div>
                    `;
                });

                list.innerHTML = html;
            }

            updateSelectedTagsCount();
        }

        function updateSelectedTagsCount() {
            const countElement = document.getElementById('selectedTagsCount');
            if (selectedTags.size > 0) {
                countElement.textContent = selectedTags.size;
                countElement.style.display = 'inline-block';
            } else {
                countElement.style.display = 'none';
            }
        }

        function updateTagButtons() {
            document.querySelectorAll('.tag-btn').forEach(btn => {
                const tag = btn.textContent.trim();
                if (selectedTags.has(tag)) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
        }

        function removeSelectedTag(tag) {
            selectedTags.delete(tag);
            updateSelectedTagsDisplay();
            updateTagButtons();
            filterContent();
        }

        function filterContent() {
            const searchInput = document.getElementById('searchInput');
            const searchTerm = searchInput.value.toLowerCase().trim();

            const containers = {
                'contests': '.contest-item[data-type="contest"]',
                'trainings': '.contest-item[data-type="training"]',
                'team': '.contest-item[data-type="team"]',
                'math': '.contest-item[data-type="math"]',
                'news': '.contest-item[data-type="news"]'
            };

            if (currentTab in containers) {
                const items = document.querySelectorAll(containers[currentTab]);
                let visibleCount = 0;

                items.forEach(item => {
                    const id = item.dataset.id.toLowerCase();
                    const title = item.dataset.title;
                    const tags = item.dataset.tags ? item.dataset.tags.split(',').map(t => t.trim().toLowerCase()) : [];

                    // Проверяем соответствие тегам
                    let matchesTags = true;
                    if (selectedTags.size > 0) {
                        // Хотя бы один из выбранных тегов должен присутствовать в тегах элемента
                        matchesTags = Array.from(selectedTags).some(selectedTag => 
                            tags.some(itemTag => itemTag === selectedTag.toLowerCase())
                        );
                    }

                    // Проверяем соответствие текстовому поиску
                    let matchesText = true;
                    if (searchTerm) {
                        matchesText = id.includes(searchTerm) || 
                                     title.includes(searchTerm) ||
                                     tags.some(tag => tag.includes(searchTerm));
                    }

                    const shouldShow = matchesTags && matchesText;
                    item.style.display = shouldShow ? 'block' : 'none';

                    if (shouldShow) {
                        visibleCount++;
                    }
                });

                // Показываем сообщение, если ничего не найдено
                const container = document.getElementById(currentTab + 'Container');
                let noResultsMsg = container.querySelector('.no-results-message');

                if (visibleCount === 0) {
                    if (!noResultsMsg) {
                        noResultsMsg = document.createElement('div');
                        noResultsMsg.className = 'contest-item no-results-message';
                        noResultsMsg.style.textAlign = 'center';
                        noResultsMsg.style.padding = '40px 20px';
                        noResultsMsg.style.color = '#999';
                        noResultsMsg.innerHTML = `
                            <i class="fas fa-search" style="font-size: 48px; margin-bottom: 15px;"></i>
                            <h3>Ничего не найдено</h3>
                            <p>Попробуйте изменить параметры поиска или фильтрации</p>
                        `;
                        container.appendChild(noResultsMsg);
                    }
                } else if (noResultsMsg) {
                    noResultsMsg.remove();
                }
            }

            // Фильтрация пользователей по поиску
            const userItems = document.querySelectorAll('.rating-item');
            userItems.forEach(item => {
                const user = item.dataset.user.toLowerCase();
                const matches = !searchTerm || user.includes(searchTerm);
                item.style.display = matches ? 'flex' : 'none';
            });
        }

        function showUpcomingContestDetails(contestId) {
            viewContestDetails(contestId);
        }

        // Закрытие выпадающего списка тегов при клике вне его
        document.addEventListener('click', function(event) {
            const tagDropdown = document.getElementById('tagDropdown');
            const tagToggle = document.getElementById('tagFilterToggle');

            if (tagDropdown && tagToggle && 
                !tagDropdown.contains(event.target) && 
                !tagToggle.contains(event.target)) {
                tagDropdown.classList.remove('active');
                tagToggle.classList.remove('active');
            }
        });

        // Закрытие выпадающего списка тегов при нажатии ESC
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const tagDropdown = document.getElementById('tagDropdown');
                const tagToggle = document.getElementById('tagFilterToggle');

                if (tagDropdown && tagDropdown.classList.contains('active')) {
                    tagDropdown.classList.remove('active');
                    tagToggle.classList.remove('active');
                }
            }
        });

        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const userParam = urlParams.get('user');
            const tabParam = urlParams.get('tab');

            if (tabParam) {
                showTab(tabParam);
            }

            if (userParam) {
                setTimeout(() => showUserGraph(userParam), 500);
            }

            // Применяем фильтрацию после загрузки
            setTimeout(filterContent, 100);
        });

        // Остальные функции (viewMathDetails, viewContestMonitor и т.д.) остаются без изменений
        // ... (они должны быть вставлены сюда из оригинального кода) ...

        function viewMathDetails(mathId) {
            fetch(`/api/math/${mathId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const modal = document.getElementById('mathModal');
                        const modalContent = document.getElementById('mathModalContent');
                        const math = data.math;

                        modalContent.innerHTML = `
                            <h2><i class="fas fa-square-root-alt"></i> ${math.title}</h2>
                            <div style="color: #666; margin: 10px 0;">
                                <i class="far fa-calendar"></i> ${math.date} • 
                                <i class="fas fa-user"></i> ${math.author}
                                ${math.pages ? `• <i class="fas fa-file-alt"></i> ${math.pages} страниц` : ''}
                            </div>

                            ${math.description ? `
                                <div class="news-content" style="margin: 15px 0;">
                                    <h3>Описание:</h3>
                                    <p>${math.description}</p>
                                </div>
                            ` : ''}

                            ${math.tags && math.tags.length > 0 ? `
                                <div style="margin: 15px 0;">
                                    <strong>Теги:</strong>
                                    <div class="tags-container">
                                        ${math.tags.map(tag => `
                                            <span class="tag math">${tag}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                <h3><i class="fas fa-file-pdf"></i> Материалы</h3>
                                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                                    <a href="/math/${mathId}/${math.filename}" target="_blank" class="contest-link" style="text-decoration: none;">
                                        <i class="fas fa-external-link-alt"></i> Открыть PDF (условия)
                                    </a>

                                    ${math.solutions_filename ? `
                                        <a href="/math/${mathId}/${math.solutions_filename}" target="_blank" class="contest-link green" style="text-decoration: none;">
                                            <i class="fas fa-chart-line"></i> Открыть решения
                                        </a>
                                    ` : ''}
                                </div>
                            </div>

                            <div style="display: flex; gap: 10px; margin-top: 20px;">
                                <button class="contest-link" onclick="closeModal('mathModal')">
                                    <i class="fas fa-times"></i> Закрыть
                                </button>
                            </div>
                        `;

                        modal.style.display = 'block';
                    }
                })
                .catch(error => {
                    alert('Ошибка загрузки информации о математике');
                });
        }

        function viewContestMonitor(contestId, division = null) {
            const modal = document.getElementById('monitorModal');
            const modalContent = document.getElementById('monitorModalContent');

            modalContent.innerHTML = `
                <h2><i class="fas fa-table"></i> Загрузка монитора...</h2>
                <p><i class="fas fa-spinner fa-spin"></i> Получение данных контеста...</p>
            `;

            modal.style.display = 'block';

            const url = `/api/contest/${contestId}/monitor${division ? `?division=${division}` : ''}`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderMonitor(data, 'contest');
                    } else {
                        modalContent.innerHTML = `
                            <h2>Ошибка</h2>
                            <p style="color: #f44336;">${data.error || 'Не удалось загрузить монитор'}</p>
                            <button class="contest-link" onclick="closeModal('monitorModal')">
                                <i class="fas fa-times"></i> Закрыть
                            </button>
                        `;
                    }
                })
                .catch(error => {
                    modalContent.innerHTML = `
                        <h2>Ошибка</h2>
                        <p style="color: #f44336;">Ошибка загрузки монитора</p>
                        <button class="contest-link" onclick="closeModal('monitorModal')">
                            <i class="fas fa-times"></i> Закрыть
                        </button>
                    `;
                });
        }

        function viewTrainingMonitor(trainingId) {
            const modal = document.getElementById('monitorModal');
            const modalContent = document.getElementById('monitorModalContent');

            modalContent.innerHTML = `
                <h2><i class="fas fa-table"></i> Загрузка монитора...</h2>
                <p><i class="fas fa-spinner fa-spin"></i> Получение данных тренировки...</p>
            `;

            modal.style.display = 'block';

            fetch(`/api/training/${trainingId}/monitor`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderMonitor(data, 'training');
                    } else {
                        modalContent.innerHTML = `
                            <h2>Ошибка</h2>
                            <p style="color: #f44336;">${data.error || 'Не удалось загрузить монитор'}</p>
                            <button class="contest-link" onclick="closeModal('monitorModal')">
                                <i class="fas fa-times"></i> Закрыть
                            </button>
                        `;
                    }
                })
                .catch(error => {
                    modalContent.innerHTML = `
                        <h2>Ошибка</h2>
                        <p style="color: #f44336;">Ошибка загрузки монитора</p>
                        <button class="contest-link" onclick="closeModal('monitorModal')">
                            <i class="fas fa-times"></i> Закрыть
                        </button>
                    `;
                });
        }

        function viewTeamMonitor(contestId) {
            const modal = document.getElementById('monitorModal');
            const modalContent = document.getElementById('monitorModalContent');

            modalContent.innerHTML = `
                <h2><i class="fas fa-table"></i> Загрузка монитора...</h2>
                <p><i class="fas fa-spinner fa-spin"></i> Получение данных командного контеста...</p>
            `;

            modal.style.display = 'block';

            fetch(`/api/team_contest/${contestId}/monitor`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        renderMonitor(data, 'team');
                    } else {
                        modalContent.innerHTML = `
                            <h2>Ошибка</h2>
                            <p style="color: #f44336;">${data.error || 'Не удалось загрузить монитор'}</p>
                            <button class="contest-link" onclick="closeModal('monitorModal')">
                                <i class="fas fa-times"></i> Закрыть
                            </button>
                        `;
                    }
                })
                .catch(error => {
                    modalContent.innerHTML = `
                        <h2>Ошибка</h2>
                        <p style="color: #f44336;">Ошибка загрузки монитора</p>
                        <button class="contest-link" onclick="closeModal('monitorModal')">
                            <i class="fas fa-times"></i> Закрыть
                        </button>
                    `;
                });
        }

        function renderMonitor(data, type) {
            const monitor = data.monitor;
            const modalContent = document.getElementById('monitorModalContent');

            let divisionsHTML = '';
            if (type === 'contest' && monitor.divisions && monitor.divisions.length > 0) {
                divisionsHTML = `
                    <div class="monitor-tabs">
                        ${monitor.divisions.map(div => `
                            <div class="monitor-tab ${div.division === monitor.current_division ? 'active' : ''}" 
                                 onclick="viewContestMonitor('${monitor.contest_id}', ${div.division})">
                                Div ${div.division}

                            </div>
                        `).join('')}
                    </div>
                `;
            }

            let statsHTML = '';
            if (monitor.stats) {
                const stats = monitor.stats;
                statsHTML = `
                    <div class="stats-summary">
                        <div class="stat-box">
                            <div class="stat-value">${stats.total_participants || stats.total_teams}</div>
                            <div class="stat-label">${type === 'team' ? 'Команд' : 'Участников'}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-value">${stats.tasks_count}</div>
                            <div class="stat-label">Задач</div>
                        </div>
                        ${type === 'contest' ? `
                            <div class="stat-box">
                                <div class="stat-value">${stats.official_participants}</div>
                                <div class="stat-label">RATED</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">${stats.unofficial_participants}</div>
                                <div class="stat-label">UNR</div>
                            </div>
                        ` : type === 'training' ? `
                            <div class="stat-box">
                                <div class="stat-value">${stats.max_solved || 0}</div>
                                <div class="stat-label">Макс. решено</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">${stats.avg_solved ? stats.avg_solved.toFixed(1) : '0.0'}</div>
                                <div class="stat-label">Среднее</div>
                            </div>
                        ` : type === 'team' ? `
                            <div class="stat-box">
                                <div class="stat-value">${stats.avg_score ? stats.avg_score.toFixed(1) : '0.0'}</div>
                                <div class="stat-label">Средний балл</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">${stats.max_score || 0}</div>
                                <div class="stat-label">Макс. балл</div>
                            </div>
                        ` : ''}
                    </div>
                `;
            }

            let tableHTML = '';
            if ((type === 'contest' || type === 'training') && monitor.participants && monitor.participants.length > 0) {
                const participants = monitor.participants;
                const taskColumns = monitor.task_names || [];

                tableHTML = `
                    <div class="monitor-container">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th class="fixed-left">#</th>
                                    <th class="fixed-left-2">${type === 'contest' ? 'Участник' : 'Участник'}</th>
                                    ${type === 'contest' ? `
                                        <th style="width: 75px; min-width: 75px; max-width: 75px;">Баллы</th>
                                        <th style="width: 75px; min-width: 75px; max-width: 75px;">Рейтинг</th>
                                        <th style="width: 75px; min-width: 75px; max-width: 75px;">Изменение</th>
                                        <th style="width: 75px; min-width: 75px; max-width: 75px;">Статус</th>
                                    ` : type === 'training' ? `
                                        <th style="width: 75px; min-width: 75px; max-width: 75px;">Решено</th>
                                        <th style="width: 75px; min-width: 75px; max-width: 75px;">Баллы</th>
                                    ` : ''}
                                    ${taskColumns.map((task, idx) => `
                                        <th class="task-header" title="${task}" style="width: 45px; min-width: 45px; max-width: 45px;">
                                            <div style="overflow: hidden; text-overflow: ellipsis; font-size: 11px;">
                                                ${String.fromCharCode(65 + idx)}
                                            </div>
                                        </th>
                                    `).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${participants.map((p, index) => {
                                    let medalClass = '';
                                    if (index === 0) medalClass = 'medal-gold';
                                    else if (index === 1) medalClass = 'medal-silver';
                                    else if (index === 2) medalClass = 'medal-bronze';

                                    return `
                                        <tr>
                                            <td class="fixed-left ${medalClass}">${index + 1}</td>
                                            <td class="fixed-left-2">
                                                <a href="javascript:void(0)" onclick="showUserGraph('${p.nickname}'); closeModal('monitorModal');" style="color: #1a73e8; text-decoration: none;">
                                                    <div style="overflow: hidden; text-overflow: ellipsis; max-width: 100%;">
                                                        ${p.nickname}
                                                    </div>
                                                </a>
                                            </td>
                                            ${type === 'contest' ? `
                                                <td style="text-align: center; font-weight: bold;">${p.score}</td>
                                                <td style="text-align: center;">${p.rating || 0}</td>
                                                <td style="text-align: center; color: ${p.change >= 0 ? '#4CAF50' : '#f44336'}; font-weight: bold;">
                                                    ${p.change >= 0 ? '+' : ''}${p.change || 0}
                                                </td>
                                                <td style="text-align: center;">
                                                    ${p.unofficial ? 
                                                        '<span class="unofficial-badge">UNR</span>' : 
                                                        '<span class="official-badge">RATED</span>'
                                                    }
                                                </td>
                                            ` : type === 'training' ? `
                                                <td style="text-align: center; font-weight: bold;">${p.solved}</td>
                                                <td style="text-align: center;">${p.points}</td>
                                            ` : ''}
                                            ${p.tasks ? p.tasks.map(task => `
                                                <td class="task-cell ${task.status}" title="${task.name}" style="width: 45px; min-width: 45px; max-width: 45px;">
                                                    <div style="width: 100%; text-align: center; overflow: hidden; text-overflow: ellipsis; font-size: 11px;">
                                                        ${task.display}
                                                    </div>
                                                </td>
                                            `).join('') : ''}
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            } else if (type === 'team' && monitor.teams && monitor.teams.length > 0) {
                const teams = monitor.teams;
                const taskColumns = monitor.task_names || [];

                tableHTML = `
                    <div class="monitor-container">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th class="fixed-left">#</th>
                                    <th class="fixed-left-2">Участник</th>
                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Баллы</th>
                                    ${taskColumns.map((task, idx) => `
                                        <th class="task-header" title="${task}" style="width: 45px; min-width: 45px; max-width: 45px;">
                                            <div style="overflow: hidden; text-overflow: ellipsis; font-size: 11px;">
                                                ${String.fromCharCode(65 + idx)}
                                            </div>
                                        </th>
                                    `).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${teams.map((team, index) => {
                                    let medalClass = '';
                                    if (index === 0) medalClass = 'medal-gold';
                                    else if (index === 1) medalClass = 'medal-silver';
                                    else if (index === 2) medalClass = 'medal-bronze';

                                    return `
                                        <tr>
                                            <td class="fixed-left ${medalClass}">${index + 1}</td>
                                            <td class="fixed-left-2">
                                                <div style="overflow: hidden; text-overflow: ellipsis; max-width: 100%;">
                                                    <strong>${team.team_name}</strong>
                                                </div>
                                            </td>
                                            <td style="text-align: center; font-weight: bold;">${team.score}</td>
                                            ${team.tasks ? team.tasks.map(task => `
                                                <td class="task-cell ${task.status}" title="${task.name}" style="width: 45px; min-width: 45px; max-width: 45px;">
                                                    <div style="width: 100%; text-align: center; overflow: hidden; text-overflow: ellipsis; font-size: 11px;">
                                                        ${task.display}
                                                    </div>
                                                </td>
                                            `).join('') : ''}
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            } else {
                tableHTML = `
                    <div style="margin: 20px 0; padding: 40px; background: #f8f9fa; border-radius: 8px; text-align: center;">
                        <i class="fas fa-info-circle" style="font-size: 48px; color: #666; margin-bottom: 15px;"></i>
                        <h3>Нет данных для отображения</h3>
                        <p>Файл monitor.csv не найден или пуст</p>
                    </div>
                `;
            }

            const title = type === 'contest' ? 
                `Монитор контеста ${monitor.contest_id.replace('contest_', '')}${monitor.current_division ? ` (Div ${monitor.current_division})` : ''}` :
                type === 'training' ?
                `Монитор тренировки ${monitor.training_id.replace('training_', '')}` :
                `Монитор командного контеста ${monitor.contest_id.replace('contest_', '')}`;

            modalContent.innerHTML = `
                <h2><i class="fas fa-table"></i> ${title}</h2>
                <div style="color: #666; margin: 10px 0;">
                    <i class="far fa-calendar"></i> ${monitor.date || 'Неизвестно'}
                    ${monitor.tasks_count ? `• <i class="fas fa-tasks"></i> ${monitor.tasks_count} задач` : ''}
                    ${monitor.total_participants ? `• <i class="fas fa-users"></i> ${monitor.total_participants} ${type === 'team' ? 'команд' : 'участников'}` : ''}
                </div>

                ${divisionsHTML}
                ${statsHTML}
                ${tableHTML}

<div style="display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap;">
    <button class="contest-link" onclick="downloadMonitor('${monitor.contest_id || monitor.training_id}', ${monitor.current_division || 0}, '${type}')">
        <i class="fas fa-download"></i> Скачать CSV
    </button>
    <button class="contest-link" onclick="printMonitor()">
        <i class="fas fa-print"></i> Печать
    </button>
    <button class="contest-link" onclick="closeModal('monitorModal')">
        <i class="fas fa-times"></i> Закрыть
    </button>
</div>
            `;
        }

        function downloadMonitor(id, division, type) {
            let url = '';
            if (type === 'contest') {
                url = `/api/contest/${id}/monitor/download${division ? `?division=${division}` : ''}`;
            } else if (type === 'training') {
                url = `/api/training/${id}/monitor/download`;
            } else if (type === 'team') {
                url = `/api/team_contest/${id}/monitor/download`;
            }
            window.open(url, '_blank');
        }

        function printMonitor() {
            const printWindow = window.open('', '_blank');
            const content = document.getElementById('monitorModalContent').innerHTML;

            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Печать монитора</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                        th { background-color: #f0f0f0; }
                        tr:nth-child(even) { background-color: #f9f9f9; }
                        .solved { background-color: #e8f5e9; color: #2e7d32; }
                        .attempted { background-color: #ffebee; color: #c62828; }
                        .unofficial-badge { background: #9C27B0; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; }
                        .official-badge { background: #e8f5e9; color: #2e7d32; padding: 2px 6px; border-radius: 4px; border: 1px solid #c8e6c9; }
                        @media print {
                            body { margin: 0; }
                            .no-print { display: none; }
                        }
                        .rating-container {
                            max-height: 350px !important;
                        }

                    </style>
                </head>
                <body>
                    ${content}
                </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.focus();
            setTimeout(() => printWindow.print(), 500);
        }

        function showUserGraph(nickname) {
            const modal = document.getElementById('chartModal');
            const modalContent = document.getElementById('modalContent');

            modalContent.innerHTML = `
                <h2><i class="fas fa-user"></i> ${nickname}</h2>
                <p><i class="fas fa-spinner fa-spin"></i> Загрузка графика рейтинга...</p>
            `;

            modal.style.display = 'block';

            fetch(`/api/user/${encodeURIComponent(nickname)}/chart`)
                .then(response => response.text())
                .then(html => {
                    modalContent.innerHTML = `
                        <h2><i class="fas fa-user"></i> ${nickname}</h2>
                        <div style="margin: 10px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <button class="contest-link" onclick="showUserDetails('${nickname}')" style="margin-right: 10px;">
                                <i class="fas fa-info-circle"></i> Подробная статистика
                            </button>
                        </div>
                        ${html}
                    `;
                })
                .catch(error => {
                    modalContent.innerHTML = `
                        <h2><i class="fas fa-user"></i> ${nickname}</h2>
                        <p style="color: #f44336;">Ошибка загрузки графика</p>
                        <button class="contest-link" onclick="showUserGraph('${nickname}')">
                            <i class="fas fa-redo"></i> Попробовать снова
                        </button>
                    `;
                });
        }

        function showUserDetails(nickname) {
            fetch(`/api/user/${encodeURIComponent(nickname)}/details`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const user = data.user;
                        const modalContent = document.getElementById('modalContent');

                        let trainingHistoryHTML = '';
                        if (user.training_history && user.training_history.length > 0) {
                            trainingHistoryHTML = `
                                <h3><i class="fas fa-dumbbell"></i> История тренировок</h3>
                                <div style="max-height: 300px; overflow-y: auto; margin: 15px 0;">
                                    <table class="results-table">
                                        <thead>
                                            <tr>
                                                <th>Тренировка</th>
                                                <th>Решено задач</th>
                                                <th>Баллы</th>
                                                <th>Дата</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${user.training_history.map(record => `
                                                <tr>
                                                    <td>${record.training.replace('training_', '')}</td>
                                                    <td style="text-align: center;">${record.solved}</td>
                                                    <td style="text-align: center;">${record.points}</td>
                                                    <td style="text-align: center;">${record.date}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            `;
                        }

                        modalContent.innerHTML = `
                            <h2><i class="fas fa-user-circle"></i> ${user.nickname}</h2>

                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0;">
                                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: #3b5998;">${user.rating}</div>
                                    <div style="font-size: 14px; color: #666;">Основной рейтинг</div>
                                </div>
                                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: #4CAF50;">${user.tasks_score}</div>
                                    <div style="font-size: 14px; color: #666;">Рейтинг решенных задач</div>
                                </div>
                                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                    <div style="font-size: 24px; font-weight: bold; color: #ff6b35;">${user.best_rating}</div>
                                    <div style="font-size: 14px; color: #666;">Лучший рейтинг</div>
                                </div>
                                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                    <div style="font-size: 20px; font-weight: bold; color: ${user.rank_color};">${user.rank}</div>
                                    <div style="font-size: 14px; color: #666;">Текущий ранг</div>
                                </div>
                            </div>

                            <h3><i class="fas fa-history"></i> История контестов</h3>
                            <div style="max-height: 300px; overflow-y: auto; margin: 15px 0;">
                                ${user.history && user.history.length > 0 ? 
                                    `<table class="results-table">
                                        <thead>
                                            <tr>
                                                <th>Контест</th>
                                                <th>Дивизион</th>
                                                <th>Место</th>
                                                <th>Прошлый рейтинг</th>
                                                <th>Новый рейтинг</th>
                                                <th>Изменение</th>
                                                <th>Статус</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${user.history.map(record => `
                                                <tr>
                                                    <td>${record.contest.replace('contest_', '')}</td>
                                                    <td style="text-align: center;">Div ${record.division}</td>
                                                    <td style="text-align: center;">${record.position}</td>
                                                    <td style="text-align: center;">${record.old_rating}</td>
                                                    <td style="text-align: center; font-weight: bold;">${record.new_rating}</td>
                                                    <td style="text-align: center; color: ${record.change >= 0 ? '#4CAF50' : '#f44336'}; font-weight: bold;">
                                                        ${record.change >= 0 ? '+' : ''}${record.change}
                                                    </td>
                                                    <td style="text-align: center;">
                                                        ${record.unofficial ? 
                                                            '<span class="unofficial-badge">UNR</span>' : 
                                                            '<span class="official-badge">RATED</span>'
                                                        }
                                                    </td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>` : 
                                    '<p style="text-align: center; color: #999; padding: 20px;">Нет истории участия</p>'
                                }
                            </div>

                            ${trainingHistoryHTML}

                            <div style="display: flex; gap: 10px; margin-top: 20px;">
                                <button class="contest-link" onclick="showUserGraph('${user.nickname}')" style="margin-right: 10px;">
                                    <i class="fas fa-chart-line"></i> Вернуться к графику
                                </button>
                                <button class="contest-link" onclick="closeModal('chartModal')">
                                    <i class="fas fa-times"></i> Закрыть
                                </button>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    alert('Ошибка загрузки данных пользователя');
                });
        }

        function viewContestDetails(contestId, division = null) {
            const modal = document.getElementById('contestModal');
            const modalContent = document.getElementById('contestModalContent');

            modalContent.innerHTML = `
                <h2><i class="fas fa-trophy"></i> Загрузка...</h2>
                <p><i class="fas fa-spinner fa-spin"></i> Получение данных контеста...</p>
            `;

            modal.style.display = 'block';

            const url = division ? `/api/contest/${contestId}?division=${division}` : `/api/contest/${contestId}`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const contest = data.contest;

                        modalContent.innerHTML = `
                            <h2><i class="fas fa-trophy"></i> ${contest.title}</h2>
                            <div style="color: #666; margin: 10px 0;">
                                <i class="far fa-calendar"></i> ${contest.date} • 
                                <i class="fas fa-users"></i> ${contest.total_participants} участников •
                                <i class="fas fa-tasks"></i> ${contest.tasks_count} задач
                            </div>

                            ${contest.tags && contest.tags.length > 0 ? `
                                <div style="margin: 10px 0;">
                                    <strong>Теги:</strong>
                                    <div class="tags-container">
                                        ${contest.tags.map(tag => `
                                            <span class="tag contest">${tag}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            ${contest.divisions && contest.divisions.length > 0 ? `
                                <div class="division-selector">
                                    <h4 style="margin: 0; line-height: 36px;">Дивизион:</h4>
                                    ${contest.divisions.map(div => `
                                        <div class="division-tab division-${div.division} ${div.division === contest.division ? 'active' : ''}" 
                                             style="background: ${div.color}; color: white;"
                                             onclick="viewContestDetails('${contestId}', ${div.division})">
                                            Div ${div.division}
                                            ${div.participants > 0 ? `<span style="margin-left: 5px; background: rgba(255,255,255,0.3); padding: 2px 6px; border-radius: 10px;">${div.participants}</span>` : ''}
                                        </div>
                                    `).join('')}
                                </div>
                            ` : ''}

                            ${contest.analysis ? `
                                <div style="margin: 10px 0;">
                                    <a href="/contest/${contestId}/${contest.analysis}" target="_blank" class="contest-link green" style="display: inline-block;">
                                        <i class="fas fa-chart-line"></i> Открыть разбор
                                    </a>
                                </div>
                            ` : ''}

                            ${contest.results && contest.results.length > 0 ? `
                                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <h3><i class="fas fa-list-ol"></i> Результаты Div ${contest.division} (${contest.results.length} участников)</h3>
                                    <div style="max-height: 400px; overflow-y: auto;">
                                        <table class="results-table">
                                            <thead>
                                                <tr>
                                                    <th class="fixed-left">Место</th>
                                                    <th class="fixed-left-2">Участник</th>
                                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Баллы</th>
                                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Рейтинг</th>
                                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Изменение</th>
                                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Статус</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${contest.results.map((p, i) => `
                                                    <tr>
                                                        <td class="fixed-left" style="text-align: center;">${i + 1}</td>
                                                        <td class="fixed-left-2">
                                                            <a href="javascript:void(0)" onclick="showUserGraph('${p.nickname}'); closeModal('contestModal');" style="color: #1a73e8; text-decoration: none;">
                                                                ${p.nickname}
                                                            </a>
                                                        </td>
                                                        <td style="text-align: center;">${p.score}</td>
                                                        <td style="text-align: center; font-weight: bold;">${p.rating || 0}</td>
                                                        <td style="text-align: center; color: ${p.change >= 0 ? '#4CAF50' : '#f44336'}; font-weight: bold;">
                                                            ${p.change >= 0 ? '+' : ''}${p.change || 0}
                                                        </td>
                                                        <td style="text-align: center;">
                                                            ${p.unofficial ? 
                                                                '<span class="unofficial-badge">UNR</span>' : 
                                                                '<span class="official-badge">RATED</span>'
                                                            }
                                                        </td>
                                                    </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ` : `
                                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: center;">
                                    <i class="fas fa-info-circle" style="font-size: 24px; color: #666; margin-bottom: 10px;"></i>
                                    <p>Нет данных о результатах для Div ${contest.division}.</p>
                                </div>
                            `}

                            <div style="display: flex; gap: 10px; margin-top: 20px;">
                                <button class="contest-link" onclick="viewContestMonitor('${contestId}', ${contest.division || 1})">
                                    <i class="fas fa-table"></i> Посмотреть монитор
                                </button>
                                <button class="contest-link" onclick="closeModal('contestModal')">
                                    <i class="fas fa-times"></i> Закрыть
                                </button>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    modalContent.innerHTML = `
                        <h2>Ошибка</h2>
                        <p style="color: #f44336;">Не удалось загрузить данные контеста</p>
                        <button class="contest-link" onclick="closeModal('contestModal')">
                            <i class="fas fa-times"></i> Закрыть
                        </button>
                    `;
                });
        }

        function viewTrainingDetails(trainingId) {
            fetch(`/api/training/${trainingId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const modal = document.getElementById('trainingModal');
                        const modalContent = document.getElementById('trainingModalContent');
                        const training = data.training;

                        modalContent.innerHTML = `
                            <h2><i class="fas fa-dumbbell"></i> ${training.title}</h2>
                            <div style="color: #666; margin: 10px 0;">
                                <i class="far fa-calendar"></i> ${training.date} • 
                                <i class="fas fa-tasks"></i> ${training.tasks_count} задач •
                                <i class="fas fa-users"></i> ${training.participants} участников
                            </div>

                            ${training.tags && training.tags.length > 0 ? `
                                <div style="margin: 10px 0;">
                                    <strong>Теги:</strong>
                                    <div class="tags-container">
                                        ${training.tags.map(tag => `
                                            <span class="tag training">${tag}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            ${training.results && training.results.length > 0 ? `
                                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <h3><i class="fas fa-list-ol"></i> Результаты (${training.results.length} участников)</h3>
                                    <div style="max-height: 400px; overflow-y: auto;">
                                        <table class="results-table">
                                            <thead>
                                                <tr>
                                                    <th class="fixed-left">Место</th>
                                                    <th class="fixed-left-2">Участник</th>
                                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Решено задач</th>
                                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Баллы</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${training.results.map((p, i) => `
                                                    <tr>
                                                        <td class="fixed-left" style="text-align: center;">${i + 1}</td>
                                                        <td class="fixed-left-2">
                                                            <a href="javascript:void(0)" onclick="showUserGraph('${p.nickname}'); closeModal('trainingModal');" style="color: #1a73e8; text-decoration: none;">
                                                                ${p.nickname}
                                                            </a>
                                                        </td>
                                                        <td style="text-align: center;">${p.solved}</td>
                                                        <td style="text-align: center;">${p.points}</td>
                                                    </tr>
                                                `).join('')}
                                            </tbody>
                                    </table>
                                    </div>
                                </div>
                            ` : `
                                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: center;">
                                    <i class="fas fa-info-circle" style="font-size: 24px; color: #666; margin-bottom: 10px;"></i>
                                    <p>Нет данных о результатах.</p>
                                </div>
                            `}

                            <div style="display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap;">
                                <button class="contest-link" onclick="viewTrainingMonitor('${trainingId}')">
                                    <i class="fas fa-table"></i> Посмотреть монитор
                                </button>
                                ${training.tasks_link ? 
                                    `<a href="${training.tasks_link}" target="_blank" class="contest-link">
                                        <i class="fas fa-file-alt"></i> Условия задач
                                    </a>` : ''
                                }
                                ${training.link ? 
                                    `<a href="${training.link}" target="_blank" class="contest-link">
                                        <i class="fas fa-external-link-alt"></i> Тренировка
                                    </a>` : ''
                                }
                                ${training.analysis ? 
                                    `<a href="/training/${trainingId}/${training.analysis}" target="_blank" class="contest-link green">
                                        <i class="fas fa-chart-line"></i> Разбор
                                    </a>` : ''
                                }
                                ${training.video ? 
                                    `<a href="${training.video}" target="_blank" class="contest-link">
                                        <i class="fas fa-video"></i> Видео
                                    </a>` : ''
                                }
                                <button class="contest-link" onclick="closeModal('trainingModal')">
                                    <i class="fas fa-times"></i> Закрыть
                                </button>
                            </div>
                        `;

                        modal.style.display = 'block';
                    }
                })
                .catch(error => {
                    alert('Ошибка загрузки данных тренировки');
                });
        }

        function viewTeamDetails(contestId) {
            fetch(`/api/team_contest/${contestId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const modal = document.getElementById('teamModal');
                        const modalContent = document.getElementById('teamModalContent');
                        const contest = data.contest;

                        modalContent.innerHTML = `
                            <h2><i class="fas fa-users"></i> ${contest.title}</h2>
                            <div style="color: #666; margin: 10px 0;">
                                <i class="far fa-calendar"></i> ${contest.date} • 
                                <i class="fas fa-tasks"></i> ${contest.tasks_count} задач •
                                <i class="fas fa-users"></i> ${contest.teams} участников
                            </div>

                            ${contest.tags && contest.tags.length > 0 ? `
                                <div style="margin: 10px 0;">
                                    <strong>Теги:</strong>
                                    <div class="tags-container">
                                        ${contest.tags.map(tag => `
                                            <span class="tag team">${tag}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            ${contest.results && contest.results.length > 0 ? `
                                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <h3><i class="fas fa-list-ol"></i> Результаты (${contest.results.length} участников)</h3>
                                    <div style="max-height: 400px; overflow-y: auto;">
                                        <table class="results-table">
                                            <thead>
                                                <tr>
                                                    <th class="fixed-left">Место</th>
                                                    <th class="fixed-left-2">Участник</th>
                                                    <th style="width: 75px; min-width: 75px; max-width: 75px;">Баллы</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${contest.results.map((team, i) => `
                                                    <tr>
                                                        <td class="fixed-left" style="text-align: center;">${i + 1}</td>
                                                        <td class="fixed-left-2">
                                                            <strong>${team.team_name}</strong>
                                                        </td>
                                                        <td style="text-align: center; font-weight: bold;">${team.score}</td>
                                                    </tr>
                                                `).join('')}
                                           </tbody>
                                        </table>
                                    </div>
                                </div>
                            ` : `
                                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: center;">
                                    <i class="fas fa-info-circle" style="font-size: 24px; color: #666; margin-bottom: 10px;"></i>
                                    <p>Нет данных о результатах.</p>
                                </div>
                            `}

                            <div style="display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap;">
                                <button class="contest-link" onclick="viewTeamMonitor('${contestId}')">
                                    <i class="fas fa-table"></i> Посмотреть монитор
                                </button>
                                ${contest.analysis ? 
                                    `<a href="/team_contest/${contestId}/${contest.analysis}" target="_blank" class="contest-link green">
                                        <i class="fas fa-chart-line"></i> Разбор
                                    </a>` : ''
                                }
                                ${contest.link ? 
                                    `<a href="${contest.link}" target="_blank" class="contest-link">
                                        <i class="fas fa-external-link-alt"></i> Контест
                                    </a>` : ''
                                }
                                <button class="contest-link" onclick="closeModal('teamModal')">
                                    <i class="fas fa-times"></i> Закрыть
                                </button>
                            </div>
                        `;

                        modal.style.display = 'block';
                    }
                })
                .catch(error => {
                    alert('Ошибка загрузки данных командного контеста');
                });
        }

        function viewNews(newsId) {
            fetch(`/api/news/${newsId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const modal = document.getElementById('newsModal');
                        const modalContent = document.getElementById('newsModalContent');
                        const news = data.news;

                        modalContent.innerHTML = `
                            <h2><i class="fas fa-newspaper"></i> ${news.title}</h2>
                            <div style="color: #666; margin: 10px 0;">
                                <i class="far fa-calendar"></i> ${news.date} • 
                                <i class="fas fa-user"></i> ${news.author}
                                ${news.priority === 'high' ? 
                                    `<span style="margin-left: 10px; background: #f44336; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                        <i class="fas fa-exclamation-triangle"></i> Важно
                                    </span>` : 
                                news.priority === 'medium' ? 
                                    `<span style="margin-left: 10px; background: #ff9800; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
                                        <i class="fas fa-info-circle"></i> Информация
                                    </span>` : ''
                                }
                            </div>

                            ${news.tags && news.tags.length > 0 ? `
                                <div style="margin: 10px 0;">
                                    <strong>Теги:</strong>
                                    <div class="tags-container">
                                        ${news.tags.map(tag => `
                                            <span class="tag news">${tag}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            <div class="news-content">
                                ${news.content}
                            </div>

                            ${news.attachments && news.attachments.length > 0 ? `
                                <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                    <h3><i class="fas fa-paperclip"></i> Вложения</h3>
                                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                                        ${news.attachments.map(attachment => `
                                            <a href="/news/${newsId}/${attachment.filename}" target="_blank" class="contest-link" style="text-decoration: none;">
                                                <i class="fas ${attachment.icon}"></i> ${attachment.name}
                                            </a>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            <div style="display: flex; gap: 10px; margin-top: 20px;">
                                <button class="contest-link" onclick="closeModal('newsModal')">
                                    <i class="fas fa-times"></i> Закрыть
                                </button>
                            </div>
                        `;

                        modal.style.display = 'block';
                    }
                })
                .catch(error => {
                    alert('Ошибка загрузки новости');
                });
        }

        function viewNewsAttachments(newsId) {
            fetch(`/api/news/${newsId}/attachments`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const modal = document.getElementById('newsModal');
                        const modalContent = document.getElementById('newsModalContent');
                        const attachments = data.attachments;

                        modalContent.innerHTML = `
                            <h2><i class="fas fa-paperclip"></i> Вложения новости</h2>

                            <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                                    ${attachments.map(attachment => `
                                        <a href="/news/${newsId}/${attachment.filename}" target="_blank" class="contest-link" style="text-decoration: none; min-width: 200px;">
                                            <div style="text-align: center; padding: 15px;">
                                                <i class="fas ${attachment.icon}" style="font-size: 32px; color: #666; margin-bottom: 10px;"></i>
                                                <div style="font-weight: bold;">${attachment.name}</div>
                                                <div style="font-size: 12px; color: #999; margin-top: 5px;">
                                                    ${attachment.size ? attachment.size + ' KB' : ''}
                                                </div>
                                            </div>
                                        </a>
                                    `).join('')}
                                </div>
                            </div>

                            <div style="display: flex; gap: 10px; margin-top: 20px;">
                                <button class="contest-link" onclick="viewNews('${newsId}')">
                                    <i class="fas fa-arrow-left"></i> Вернуться к новости
                                </button>
                                <button class="contest-link" onclick="closeModal('newsModal')">
                                    <i class="fas fa-times"></i> Закрыть
                                </button>
                            </div>
                        `;

                        modal.style.display = 'block';
                    }
                })
                .catch(error => {
                    alert('Ошибка загрузки вложений');
                });
        }

        function processContest(contestId) {
            if (confirm(`Обработать контест ${contestId}?`)) {
                fetch(`/api/contest/${contestId}/process-all`, { 
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            location.reload();
                        } else {
                            alert(data.error || 'Ошибка обработки контеста');
                        }
                    })
                    .catch(error => {
                        alert('Ошибка обработки контеста');
                    });
            }
        }

        function processTraining(trainingId) {
            if (confirm(`Обработать тренировку ${trainingId}?`)) {
                fetch(`/api/training/${trainingId}/process`, { 
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            location.reload();
                        } else {
                            alert(data.error || 'Ошибка обработки тренировки');
                        }
                    })
                    .catch(error => {
                        alert('Ошибка обработки тренировки');
                    });
            }
        }

        function processTeamContest(contestId) {
            if (confirm(`Обработать командный контест ${contestId}?`)) {
                fetch(`/api/team_contest/${contestId}/process`, { 
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            location.reload();
                        } else {
                            alert(data.error || 'Ошибка обработки командного контеста');
                        }
                    })
                    .catch(error => {
                        alert('Ошибка обработки командного контеста');
                    });
            }
        }

        function showAllUsers() {
            window.open('/users', '_blank');
        }

        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }

        window.onclick = function(event) {
            const chartModal = document.getElementById('chartModal');
            const contestModal = document.getElementById('contestModal');
            const trainingModal = document.getElementById('trainingModal');
            const teamModal = document.getElementById('teamModal');
            const mathModal = document.getElementById('mathModal');
            const monitorModal = document.getElementById('monitorModal');
            const newsModal = document.getElementById('newsModal');

            if (event.target == chartModal) closeModal('chartModal');
            if (event.target == contestModal) closeModal('contestModal');
            if (event.target == trainingModal) closeModal('trainingModal');
            if (event.target == teamModal) closeModal('teamModal');
            if (event.target == mathModal) closeModal('mathModal');
            if (event.target == monitorModal) closeModal('monitorModal');
            if (event.target == newsModal) closeModal('newsModal');
        }
    </script>
</body>
</html>
'''


class DivisionSystem:
    DIVISION_RANGES = {
        1: (3000, 4000),
        2: (2000, 2999),
        3: (1000, 1999),
        4: (0, 999),
    }

    DIVISION_COLORS = {
        1: '#FF0000',
        2: '#FF9800',
        3: '#4CAF50',
        4: '#2196F3',
    }

    @staticmethod
    def get_division(rating):
        """Определяет дивизион по рейтингу"""
        for div_num, (min_rating, max_rating) in DivisionSystem.DIVISION_RANGES.items():
            if min_rating <= rating <= max_rating:
                return div_num
        # Если рейтинг выше 4000 или отрицательный
        if rating > 4000:
            return 1
        elif rating < 0:
            return 4
        return 4

    @staticmethod
    def is_rating_in_division(rating, division):
        """Проверяет, находится ли рейтинг в указанном дивизионе"""
        if division not in DivisionSystem.DIVISION_RANGES:
            return False
        min_rating, max_rating = DivisionSystem.DIVISION_RANGES[division]
        return min_rating <= rating <= max_rating


class RatingSystem:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.contests_path = self.base_path / 'contests'
        self.trainings_path = self.base_path / 'trainings'
        self.team_contests_path = self.base_path / 'team_contests'
        self.contestants_path = self.base_path / 'contestants'

        self.users = {}  # {nickname: {'rating': int, 'tasks_score': int}}
        self.user_history = {}  # История контестов пользователя
        self.user_training_history = {}

        self.contests_path.mkdir(parents=True, exist_ok=True)
        self.trainings_path.mkdir(parents=True, exist_ok=True)
        self.team_contests_path.mkdir(parents=True, exist_ok=True)
        self.contestants_path.mkdir(parents=True, exist_ok=True)

        self.load_all_data()

    # ========== ОСНОВНЫЕ МЕТОДЫ ==========

    def get_user_rating(self, nickname):
        """Возвращает текущий рейтинг пользователя"""
        if nickname not in self.users:
            return 0
        return self.users[nickname].get('rating', 0)

    def get_user_division(self, nickname):
        """Определяет дивизион пользователя по его текущему рейтингу"""
        rating = self.get_user_rating(nickname)

        if rating < 0:
            return 4
        elif 0 <= rating <= 999:
            return 4
        elif 1000 <= rating <= 1999:
            return 3
        elif 2000 <= rating <= 2999:
            return 2
        elif 3000 <= rating <= 4000:
            return 1
        else:
            return 1  # Если рейтинг выше 4000 - Div1

    def get_user_max_rating(self, nickname):
        """Возвращает максимальный рейтинг пользователя из истории"""
        if nickname not in self.user_history:
            return self.get_user_rating(nickname)

        max_rating = 0
        for record in self.user_history[nickname]:
            if not record.get('unofficial', False):
                new_rating = record.get('new_rating', 0)
                if new_rating > max_rating:
                    max_rating = new_rating

        current_rating = self.get_user_rating(nickname)
        return max(max_rating, current_rating)

    def get_user_tasks_score(self, nickname):
        if nickname not in self.users:
            return 0
        return self.users[nickname].get('tasks_score', 0)

    def get_rank_title(self, rating):
        if rating < 400:
            return "Новичок"
        elif rating < 800:
            return "Ученик"
        elif rating < 1200:
            return "Практик"
        elif rating < 1600:
            return "Специалист"
        elif rating < 2000:
            return "Эксперт"
        elif rating < 2400:
            return "Кандидат в мастера"
        elif rating < 2800:
            return "Мастер"
        elif rating < 3200:
            return "Грандмастер"
        elif rating < 3600:
            return "Легендарный мастер"
        else:
            return "Абсолютный мастер"

    def get_rank_color(self, rating):
        if rating < 400:
            return "#804000"
        elif rating < 800:
            return "#808080"
        elif rating < 1200:
            return "#008000"
        elif rating < 1600:
            return "#00C0C0"
        elif rating < 2000:
            return "#0000FF"
        elif rating < 2400:
            return "#AA00AA"
        elif rating < 2800:
            return "#C0C000"
        elif rating < 3200:
            return "#FF8000"
        elif rating < 3600:
            return "#FF0000"
        else:
            return "#FF0066"

    def get_avatar_color(self, nickname):
        hash_val = sum(ord(c) for c in nickname) % 360
        return f'hsl({hash_val}, 70%, 60%)'

    def get_user_stats(self, nickname):
        """Возвращает статистику пользователя"""
        if nickname not in self.users:
            return None

        current_rating = self.get_user_rating(nickname)
        tasks_score = self.get_user_tasks_score(nickname)
        history = self.user_history.get(nickname, [])
        training_history = self.user_training_history.get(nickname, [])

        official_history = [h for h in history if not h.get('unofficial', False)]

        best_rating = self.get_user_max_rating(nickname)

        last_contest = "Нет"
        if official_history:
            def contest_number_key(record):
                contest_id = record.get('contest', '')
                match = re.search(r'contest_(\d+)', contest_id)
                if match:
                    return int(match.group(1))
                return 0

            sorted_history = sorted(official_history, key=contest_number_key, reverse=True)
            if sorted_history:
                last_record = sorted_history[0]
                last_contest = last_record['contest'].replace('contest_', '')

        return {
            'nickname': nickname,
            'rating': current_rating,
            'division': self.get_user_division(nickname),
            'tasks_score': tasks_score,
            'best_rating': best_rating,
            'contests': len(official_history),
            'unofficial_contests': len([h for h in history if h.get('unofficial', False)]),
            'last_contest': last_contest,
            'rank': self.get_rank_title(current_rating),
            'rank_color': self.get_rank_color(current_rating),
            'avatar_color': self.get_avatar_color(nickname),
            'avatar_text': nickname[:2].upper() if len(nickname) >= 2 else nickname[0].upper(),
            'history': sorted(official_history, key=lambda x: (
                -int(re.search(r'contest_(\d+)', x.get('contest', '')).group(1))
                if re.search(r'contest_(\d+)', x.get('contest', '')) else 0
            )),
            'training_history': sorted(training_history, key=lambda x: (
                -int(re.search(r'training_(\d+)', x.get('training', '')).group(1))
                if re.search(r'training_(\d+)', x.get('training', '')) else 0
            ))
        }

    # ========== ЗАГРУЗКА И СОХРАНЕНИЕ ДАННЫХ ==========

    def load_all_data(self):
        ratings_file = self.contestants_path / 'all_ratings.txt'

        if ratings_file.exists():
            try:
                with open(ratings_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                if content:
                    self.load_ratings_from_file(ratings_file)
                else:
                    self.load_history_from_contests()
                    self.recalculate_ratings_from_history()
                    self.save_ratings()
            except Exception as e:
                self.load_history_from_contests()
                self.recalculate_ratings_from_history()
                self.save_ratings()
        else:
            self.load_history_from_contests()
            self.recalculate_ratings_from_history()
            self.save_ratings()

    def load_ratings_from_file(self, ratings_file):
        try:
            self.users = {}
            self.user_history = {}
            self.user_training_history = {}

            with open(ratings_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue

                    parts = line.split(':', 1)
                    nickname = parts[0].strip()
                    data_str = parts[1].strip()

                    try:
                        data = json.loads(data_str)

                        rating = data.get('rating', 0)
                        tasks_score = data.get('tasks_score', 0)

                        self.users[nickname] = {
                            'rating': int(rating),
                            'tasks_score': int(tasks_score)
                        }

                        contest_history = data.get('contest_history', [])
                        self.user_history[nickname] = contest_history

                        training_history = data.get('training_history', [])
                        self.user_training_history[nickname] = training_history
                    except:
                        self.users[nickname] = {'rating': 0, 'tasks_score': 0}
                        self.user_history[nickname] = []
                        self.user_training_history[nickname] = []
        except:
            self.users = {}
            self.user_history = {}
            self.user_training_history = {}

    def save_ratings(self):
        ratings_file = self.contestants_path / 'all_ratings.txt'
        try:
            temp_file = ratings_file.with_suffix('.tmp')

            with open(temp_file, 'w', encoding='utf-8') as f:
                sorted_users = sorted(
                    self.users.items(),
                    key=lambda x: x[1].get('rating', 0),
                    reverse=True
                )

                for nickname, user_data in sorted_users:
                    user_info = {
                        'rating': user_data.get('rating', 0),
                        'tasks_score': user_data.get('tasks_score', 0),
                        'contest_history': self.user_history.get(nickname, []),
                        'training_history': self.user_training_history.get(nickname, [])
                    }

                    json_str = json.dumps(user_info, ensure_ascii=False)
                    f.write(f"{nickname}: {json_str}\n")

            if temp_file.exists():
                if ratings_file.exists():
                    ratings_file.unlink()
                temp_file.rename(ratings_file)
        except Exception as e:
            print(f"Ошибка сохранения рейтингов: {e}")

    # ========== ГЕНЕРАЦИЯ ФАЙЛОВ ИЗМЕНЕНИЙ ==========

    def generate_change_file(self, contest_dir, division):
        """Генерирует change.txt для дивизиона контеста"""
        contest_id = contest_dir.name
        division_dir = contest_dir / f'div{division}'

        if not division_dir.exists():
            return False, f"Папка div{division} не найдена"

        monitor_file = division_dir / 'monitor.csv'
        change_file = division_dir / 'change.txt'

        if not monitor_file.exists():
            return False, f"Файл monitor.csv не найден в div{division}"

        try:
            participants = []

            # Сначала читаем всех участников из монитора
            with open(monitor_file, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)

                if ';' in sample:
                    reader = csv.DictReader(f, delimiter=';')
                else:
                    reader = csv.DictReader(f)

                for i, row in enumerate(reader):
                    nickname = row.get('user_name', '') or row.get('login', '') or row.get('Участник', '')
                    if nickname and nickname.strip():
                        nickname = nickname.strip()

                        score_str = row.get('Score', '0') or row.get('score', '0') or row.get('Баллы', '0')
                        try:
                            score = float(score_str)
                        except:
                            score = 0

                        tasks_solved = 0
                        for key, value in row.items():
                            if key.lower() not in ['place', 'user_name', 'login', 'Участник', 'участник',
                                                   'Score', 'Penalty', 'score', 'penalty', 'Баллы', 'баллы',
                                                   'user', 'User', 'USER', 'фио', 'ФИО']:
                                if value and ('+' in str(value) or str(value).isdigit() and int(value) > 0):
                                    tasks_solved += 1

                        # Получаем текущий рейтинг пользователя
                        current_rating = self.get_user_rating(nickname)

                        # Определяем разрешенный дивизион пользователя
                        allowed_division = self.get_user_division(nickname)

                        # Определяем unofficial статус
                        # Участник официальный ТОЛЬКО если пишет в своем allowed_division
                        unofficial = (division != allowed_division)

                        participants.append({
                            'nickname': nickname,
                            'score': score,
                            'tasks_solved': tasks_solved,
                            'rating': current_rating,
                            'unofficial': unofficial,
                            'allowed_division': allowed_division,
                            'current_division': division
                        })

            if not participants:
                return False, f"Нет участников в monitor.csv для Div {division}"

            participants.sort(key=lambda x: x['score'], reverse=True)

            # Только официальные участники для подсчета рейтинга
            official_participants = [p for p in participants if not p['unofficial']]
            total_official = len(official_participants)

            with open(change_file, 'w', encoding='utf-8') as f:
                f.write(f"Контест: {contest_id}\n")
                f.write(f"Дивизион: {division}\n")
                f.write(f"Дата обработки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Участников всего: {len(participants)}\n")
                f.write(f"Участников официально: {total_official}\n")
                f.write(f"Unofficial участников: {len(participants) - total_official}\n")
                f.write("=" * 60 + "\n")

                all_participants_sorted = sorted(participants, key=lambda x: x['score'], reverse=True)

                official_counter = 0
                for i, participant in enumerate(all_participants_sorted):
                    nickname = participant['nickname']
                    old_rating = participant['rating']
                    unofficial = participant['unofficial']
                    tasks_solved = participant['tasks_solved']
                    allowed_division = participant['allowed_division']

                    if unofficial:
                        delta = 0
                        new_rating = old_rating
                        status = "UNRATED"
                    else:
                        official_counter += 1
                        delta = self.calculate_rating_change(official_counter, total_official, old_rating, tasks_solved)
                        new_rating = max(0, old_rating + delta)
                        status = "RATED"

                    rank_old = self.get_rank_title(old_rating)
                    rank_new = self.get_rank_title(new_rating)

                    tasks_info = f" (задач: {tasks_solved})" if tasks_solved > 0 else ""

                    # Отладочная информация
                    debug_info = ""
                    if unofficial:
                        debug_info = f" [unofficial: allowed_div={allowed_division}, current_div={division}]"

                    f.write(f"{i + 1:3d}. {nickname}: {old_rating:4d} ({rank_old}) → "
                            f"{new_rating:4d} ({rank_new}) ({delta:+d}) {status}{tasks_info}{debug_info}\n")

            # Обновляем рейтинги участников
            official_counter = 0
            for i, participant in enumerate(all_participants_sorted):
                nickname = participant['nickname']
                old_rating = participant['rating']
                unofficial = participant['unofficial']
                tasks_solved = participant['tasks_solved']
                allowed_division = participant['allowed_division']

                if nickname not in self.user_history:
                    self.user_history[nickname] = []

                already_processed = False
                for record in self.user_history[nickname]:
                    if record['contest'] == contest_id and record['division'] == division:
                        already_processed = True
                        break

                if not already_processed:
                    if unofficial:
                        delta = 0
                        new_rating = old_rating
                    else:
                        official_counter += 1
                        delta = self.calculate_rating_change(official_counter, total_official, old_rating, tasks_solved)
                        new_rating = max(0, old_rating + delta)

                    # Сохраняем историю контеста
                    self.user_history[nickname].append({
                        'contest': contest_id,
                        'division': division,
                        'position': i + 1,
                        'old_rating': old_rating,
                        'new_rating': new_rating,
                        'change': delta,
                        'tasks_solved': tasks_solved,
                        'unofficial': unofficial,
                        'allowed_division': allowed_division,
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'type': 'contest'
                    })

                    # Обновляем рейтинг только если участник официальный
                    if not unofficial:
                        # Инициализируем пользователя если его нет
                        if nickname not in self.users:
                            self.users[nickname] = {'rating': 0, 'tasks_score': 0}

                        # Обновляем единый рейтинг
                        self.users[nickname]['rating'] = new_rating

                        # Обновляем счетчик решенных задач
                        self.users[nickname]['tasks_score'] = self.users[nickname].get('tasks_score', 0) + tasks_solved

            self.save_ratings()

            return True, f"Файл change.txt успешно создан для {contest_id}, Div {division}"
        except Exception as e:
            import traceback
            return False, f"Ошибка генерации change.txt: {str(e)}\n{traceback.format_exc()}"

    # ========== РАСЧЕТ ИЗМЕНЕНИЯ РЕЙТИНГА ==========

    def calculate_rating_change(self, place, total_participants, old_rating, tasks_solved=0):
        if total_participants <= 1:
            return 0

        percentile = 100 * (total_participants - place) / total_participants

        expected_performance = 0
        if percentile >= 99:
            expected_performance = 2400
        elif percentile >= 90:
            expected_performance = 2100
        elif percentile >= 80:
            expected_performance = 1900
        elif percentile >= 70:
            expected_performance = 1700
        elif percentile >= 60:
            expected_performance = 1500
        elif percentile >= 50:
            expected_performance = 1350
        elif percentile >= 40:
            expected_performance = 1200
        elif percentile >= 30:
            expected_performance = 1050
        elif percentile >= 20:
            expected_performance = 900
        elif percentile >= 10:
            expected_performance = 750
        else:
            expected_performance = 600

        task_bonus = tasks_solved * 25

        if old_rating == 0:
            delta = (expected_performance + task_bonus - 1000) * 0.5
        else:
            delta = (expected_performance + task_bonus - old_rating) * 0.2

        if delta > 0:
            delta = min(400, delta)
        else:
            delta = max(-400, delta)

        if place == 1 and delta < 150:
            delta = 150
        elif place <= 3 and delta < 100:
            delta = 100
        elif place <= total_participants * 0.1 and delta < 50:
            delta = 50

        if place >= total_participants * 0.9 and delta > -50:
            delta = -50
        elif place == total_participants and delta > -100:
            delta = -100

        return int(round(delta))

    # ========== ОБРАБОТКА КОНТЕСТОВ ==========

    def process_division(self, contest_id, division):
        contest_dir = self.contests_path / contest_id
        if not contest_dir.exists():
            return False, "Контест не найден"

        success, message = self.generate_change_file(contest_dir, division)
        return success, message

    def process_all_divisions(self, contest_id):
        contest_dir = self.contests_path / contest_id
        if not contest_dir.exists():
            return False, "Контест не найден"

        results = []
        for division in range(1, 5):
            division_dir = contest_dir / f'div{division}'
            if division_dir.exists():
                monitor_file = division_dir / 'monitor.csv'
                if monitor_file.exists():
                    success, message = self.generate_change_file(contest_dir, division)
                    if success:
                        results.append(f"Div {division}: Успешно")
                    else:
                        results.append(f"Div {division}: Ошибка - {message}")

        if results:
            return True, f"Обработаны дивизионы:\n" + "\n".join(results)
        else:
            return False, "Нет данных для обработки"

    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========

    def load_history_from_contests(self):
        for contest_dir in self.contests_path.glob('contest_*'):
            if contest_dir.is_dir():
                for division in range(1, 5):
                    division_dir = contest_dir / f'div{division}'
                    change_file = division_dir / 'change.txt'
                    if change_file.exists():
                        self.read_change_file(contest_dir.name, division, change_file)

        for training_dir in self.trainings_path.glob('training_*'):
            if training_dir.is_dir():
                change_file = training_dir / 'change.txt'
                if change_file.exists():
                    self.read_training_change_file(training_dir.name, change_file)

    def read_change_file(self, contest_id, division, change_file):
        """Читает историю из change.txt"""
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            start_line = 0
            for i, line in enumerate(lines):
                if '=====' in line:
                    start_line = i + 1
                    break

            for line in lines[start_line:]:
                line = line.strip()
                if not line:
                    continue

                match = re.match(
                    r'(\d+)\.\s+([^:]+):\s+(\d+)\s+\([^)]+\)\s+→\s+(\d+)\s+\([^)]+\)\s+\(([+-]\d+)\)',
                    line)
                if match:
                    position = int(match.group(1))
                    nickname = match.group(2).strip()
                    old_rating = int(match.group(3))
                    new_rating = int(match.group(4))
                    change = int(match.group(5))

                    if nickname not in self.users:
                        self.users[nickname] = {'rating': 0, 'tasks_score': 0}

                    unofficial = "[UNR]" in line or "UNRATED" in line or "unofficial" in line.lower()

                    tasks_solved_match = re.search(r'задач:\s+(\d+)', line)
                    tasks_solved = int(tasks_solved_match.group(1)) if tasks_solved_match else 0

                    if nickname not in self.user_history:
                        self.user_history[nickname] = []

                    already_processed = False
                    for record in self.user_history[nickname]:
                        if (record['contest'] == contest_id and
                                record['division'] == division):
                            already_processed = True
                            break

                    if not already_processed:
                        allowed_division = division
                        if "allowed_div" in line:
                            match_div = re.search(r'allowed_div:(\d+)', line)
                            if match_div:
                                allowed_division = int(match_div.group(1))

                        self.user_history[nickname].append({
                            'contest': contest_id,
                            'division': division,
                            'position': position,
                            'old_rating': old_rating,
                            'new_rating': new_rating,
                            'change': change,
                            'tasks_solved': tasks_solved,
                            'unofficial': unofficial,
                            'allowed_division': allowed_division,
                            'date': self.get_file_date(change_file),
                            'type': 'contest'
                        })

                        if not unofficial:
                            self.users[nickname]['rating'] = new_rating
                            self.users[nickname]['tasks_score'] = self.users[nickname].get('tasks_score',
                                                                                           0) + tasks_solved
        except Exception as e:
            print(f"Ошибка чтения change.txt {change_file}: {e}")

    def recalculate_ratings_from_history(self):
        """Пересчитывает текущие рейтинги из истории контестов"""
        # Сбрасываем все рейтинги
        for nickname in self.users:
            self.users[nickname] = {'rating': 0, 'tasks_score': 0}

        # Проходим по всей истории и восстанавливаем рейтинги
        for nickname, history in self.user_history.items():
            if nickname not in self.users:
                self.users[nickname] = {'rating': 0, 'tasks_score': 0}

            # Сортируем историю по номеру контеста
            def get_contest_number(record):
                contest_id = record.get('contest', '')
                match = re.search(r'contest_(\d+)', contest_id)
                if match:
                    return int(match.group(1))
                return 0

            sorted_history = sorted(history, key=get_contest_number)

            # Обрабатываем каждый контест
            for record in sorted_history:
                if not record.get('unofficial', False):
                    new_rating = record.get('new_rating', 0)
                    tasks_solved = record.get('tasks_solved', 0)

                    # Обновляем рейтинг
                    self.users[nickname]['rating'] = new_rating

                    # Добавляем баллы за задачи
                    self.users[nickname]['tasks_score'] = self.users[nickname].get('tasks_score', 0) + tasks_solved

    def get_file_date(self, change_file):
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Дата обработки:' in line:
                        date_str = line.split('Дата обработки:')[1].strip()
                        return date_str.split()[0]
        except:
            pass
        return datetime.now().strftime("%Y-%m-%d")

    def get_file_date(self, change_file):
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Дата обработки:' in line:
                        date_str = line.split('Дата обработки:')[1].strip()
                        return date_str.split()[0]
        except:
            pass
        return datetime.now().strftime("%Y-%m-%d")

    def generate_rating_chart(self, nickname, division=None):
        """Генерирует график изменения рейтинга из ЗАМОРОЖЕННОЙ истории"""
        all_events = []

        contest_history = self.user_history.get(nickname, [])
        official_contests = [h for h in contest_history if not h.get('unofficial', False)]

        for contest in official_contests:
            all_events.append({
                'type': 'contest',
                'event': contest['contest'],
                'title': f"Контест {contest['contest'].replace('contest_', '')}",
                'date': contest['date'],
                'rating': contest['new_rating'],  # Используем ЗАМОРОЖЕННЫЙ рейтинг
                'change': contest['change'],
                'division': contest.get('division'),
                'position': contest.get('position'),
                'frozen': True
            })

        def event_number_key(event):
            match = re.search(r'contest_(\d+)', event.get('event', ''))
            if match:
                return int(match.group(1))
            return 0

        all_events.sort(key=event_number_key)

        if len(all_events) < 2:
            return None

        dates = []
        ratings = []
        events_info = []

        for event in all_events:
            if event['type'] == 'contest':
                dates.append(event['event'].replace('contest_', ''))
                ratings.append(event['rating'])  # ЗАМОРОЖЕННЫЙ рейтинг
                events_info.append(event)

        date_nums = list(range(1, len(dates) + 1))

        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

        ax.plot(date_nums, ratings, 'k-', linewidth=2, alpha=0.8)
        ax.plot(date_nums, ratings, 'ko', markersize=4, markeredgecolor='k', markerfacecolor='k')

        title = f'Изменение рейтинга: {nickname}'
        if division:
            title += f' (Div {division})'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        ax.set_xlabel('Номер контеста', fontsize=12)
        ax.set_ylabel('Рейтинг', fontsize=12)

        if len(date_nums) <= 30:
            ax.set_xticks(date_nums)
            ax.set_xticklabels(dates, rotation=45, ha='right')
        else:
            step = max(1, len(date_nums) // 20)
            ax.set_xticks(date_nums[::step])
            ax.set_xticklabels(dates[::step], rotation=45, ha='right')

        ax.grid(True, alpha=0.3, linestyle='--')

        if ratings:
            y_min = max(0, min(ratings) - 100)
            y_max = min(4000, max(ratings) + 100)
            ax.set_ylim([y_min, y_max])

        current_rating = ratings[-1] if ratings else 0
        current_rank = self.get_rank_title(current_rating)
        rank_color = self.get_rank_color(current_rating)

        ax.text(0.02, 0.98, f'Текущий: {current_rating} ({current_rank})',
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                verticalalignment='top', color=rank_color,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='lightgray'))

        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)

        return base64.b64encode(buf.getvalue()).decode('utf-8')


rating_system = RatingSystem('.')


def load_contests():
    contests = []
    contests_path = Path('contests')

    if not contests_path.exists():
        return contests

    contest_folders = list(contests_path.glob('contest_*'))

    for folder in contest_folders:
        if folder.is_dir():
            contest_id = folder.name

            number_match = re.search(r'contest_(\d+)', contest_id.lower())
            number = number_match.group(1).lstrip('0') if number_match else contest_id

            tags = []
            tags_file = folder / 'tags.txt'
            if tags_file.exists():
                try:
                    with open(tags_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        tags = [tag.strip() for tag in content.split(',') if tag.strip()]
                except:
                    pass

            divisions = []
            total_participants = 0
            processed = False

            for div_num in [1, 2, 3, 4]:
                division_dir = folder / f'div{div_num}'
                if division_dir.exists():
                    link_file = division_dir / 'link.txt'
                    monitor_file = division_dir / 'monitor.csv'
                    change_file = division_dir / 'change.txt'

                    link = ""
                    if link_file.exists():
                        try:
                            with open(link_file, 'r', encoding='utf-8') as f:
                                link = f.read().strip()
                        except:
                            pass

                    # УБИРАЕМ подсчет участников для отображения на иконках
                    participants = 0  # Всегда 0, чтобы не отображалось на иконках

                    # Но сохраняем для статистики в другом месте
                    actual_participants = 0
                    if change_file.exists():
                        try:
                            with open(change_file, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if 'Участников официально:' in line:
                                        parts = line.split(':')
                                        if len(parts) > 1:
                                            try:
                                                actual_participants = int(parts[1].strip())
                                                total_participants += actual_participants
                                            except:
                                                pass
                                        break
                        except:
                            pass

                    if change_file.exists():
                        processed = True

                    if link or monitor_file.exists():
                        divisions.append({
                            'division': div_num,
                            'link': link,
                            'color': DivisionSystem.DIVISION_COLORS[div_num],
                            'participants': participants,  # Всегда 0 для скрытия на иконках
                            'actual_participants': actual_participants,  # Реальное число для внутреннего использования
                            'processed': change_file.exists(),
                            'has_monitor': monitor_file.exists()
                        })

            analysis = None
            analysis_files = list(folder.glob('*analysis*')) + list(folder.glob('*разбор*'))
            if analysis_files:
                analysis = analysis_files[0].name

            tasks_count = 0
            for div in divisions:
                if div['has_monitor']:
                    monitor_file = folder / f'div{div["division"]}' / 'monitor.csv'
                    try:
                        with open(monitor_file, 'r', encoding='utf-8') as f:
                            sample = f.read(1024)
                            f.seek(0)

                            if ';' in sample:
                                reader = csv.DictReader(f, delimiter=';')
                            else:
                                reader = csv.DictReader(f)

                            fieldnames = reader.fieldnames or []
                            exclude_fields = ['place', 'user_name', 'login', 'Участник', 'участник',
                                              'Score', 'Penalty', 'score', 'penalty', 'Баллы', 'баллы',
                                              'user', 'User', 'USER', 'фио', 'ФИО']

                            for field in fieldnames:
                                if (field not in exclude_fields and
                                        not field.startswith('Unnamed:') and
                                        not re.match(r'^(фио|ФИО|user|name|имя|никнейм)', field.lower()) and
                                        field.strip() != ''):
                                    tasks_count += 1
                            if tasks_count > 0:
                                break
                    except:
                        pass

            date = "Неизвестно"
            for div in divisions:
                if div['processed']:
                    change_file = folder / f'div{div["division"]}' / 'change.txt'
                    try:
                        with open(change_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                if 'Дата обработки:' in line:
                                    date_part = line.split('Дата обработки:')[1].strip()
                                    date = date_part.split()[0]
                                    break
                    except:
                        pass

            if date == "Неизвестно":
                match = re.search(r'(\d{4})(\d{2})(\d{2})', contest_id)
                if match:
                    year, month, day = match.groups()
                    date = f"{year}-{month}-{day}"

            date_obj = None
            if date != "Неизвестно":
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                except:
                    try:
                        date_obj = datetime.strptime(date, "%d.%m.%Y")
                    except:
                        date_obj = None

            if not date_obj:
                match = re.search(r'(\d{4})(\d{2})(\d{2})', contest_id)
                if match:
                    year, month, day = match.groups()
                    try:
                        date_obj = datetime(int(year), int(month), int(day))
                        date = f"{year}-{month}-{day}"
                    except:
                        date_obj = datetime.min

            winner = ""
            max_rating = 0
            for div in divisions:
                if div['processed']:
                    change_file = folder / f'div{div["division"]}' / 'change.txt'
                    try:
                        with open(change_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                if line.strip().startswith('1.'):
                                    winner_match = re.match(r'1\.\s+([^:]+):', line)
                                    if winner_match:
                                        winner = winner_match.group(1).strip()
                                        rating_match = re.search(r'→\s+(\d+)\s+\(', line)
                                        if rating_match:
                                            rating = int(rating_match.group(1))
                                            if rating > max_rating:
                                                max_rating = rating
                                        break
                    except:
                        pass

            contests.append({
                'id': contest_id,
                'number': number,
                'title': f"Контест {number}",
                'date': date,
                'date_obj': date_obj,
                'divisions': divisions,
                'analysis': analysis,
                'total_participants': total_participants,  # Сохраняем для общей статистики
                'winner': winner,
                'max_rating': max_rating,
                'tasks_count': tasks_count,
                'tags': tags,
                'processed': processed
            })

    contests.sort(key=lambda x: (
        int(x['number']) if x['number'].isdigit() else 0
    ), reverse=True)

    return contests


def load_trainings():
    trainings = []
    trainings_path = Path('trainings')

    if not trainings_path.exists():
        return trainings

    training_folders = list(trainings_path.glob('training_*'))

    for folder in training_folders:
        if folder.is_dir():
            training_id = folder.name

            number_match = re.search(r'training_(\d+)', training_id.lower())
            number = number_match.group(1).lstrip('0') if number_match else training_id

            tags = []
            tags_file = folder / 'tags.txt'
            if tags_file.exists():
                try:
                    with open(tags_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        tags = [tag.strip() for tag in content.split(',') if tag.strip()]
                except:
                    pass

            monitor_file = folder / 'monitor.csv'
            change_file = folder / 'change.txt'
            analysis_files = list(folder.glob('*analysis*')) + list(folder.glob('*разбор*'))
            video_file = folder / 'video.txt'
            link_file = folder / 'link.txt'

            monitor = monitor_file.name if monitor_file.exists() else None
            analysis = analysis_files[0].name if analysis_files else None

            video = None
            if video_file.exists():
                try:
                    with open(video_file, 'r', encoding='utf-8') as f:
                        video = f.read().strip()
                except:
                    pass

            link = None
            if link_file.exists():
                try:
                    with open(link_file, 'r', encoding='utf-8') as f:
                        link = f.read().strip()
                except:
                    pass

            processed = change_file.exists()

            tasks_count = 0
            if monitor_file.exists():
                try:
                    with open(monitor_file, 'r', encoding='utf-8') as f:
                        sample = f.read(1024)
                        f.seek(0)

                        if ';' in sample:
                            reader = csv.DictReader(f, delimiter=';')
                        else:
                            reader = csv.DictReader(f)

                        fieldnames = reader.fieldnames or []
                        exclude_fields = ['place', 'user_name', 'login', 'user', 'User', 'USER',
                                          'Score', 'Penalty', 'score', 'penalty', 'фио', 'ФИО']

                        for field in fieldnames:
                            if (field not in exclude_fields and
                                    not field.startswith('Unnamed:') and
                                    not re.match(r'^(фио|ФИО|user|name|имя|никнейм)', field.lower()) and
                                    field.strip() != ''):
                                tasks_count += 1
                except:
                    pass

            participants = 0
            max_points = 0
            avg_points = 0

            if change_file.exists():
                try:
                    with open(change_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            if 'Участников:' in line:
                                parts = line.split(':')
                                if len(parts) > 1:
                                    try:
                                        participants = int(parts[1].strip())
                                    except:
                                        pass
                            elif '1.' in line:
                                match = re.search(r'решено\s+(\d+)\s+задач', line)
                                if match:
                                    max_points = int(match.group(1))
                except:
                    pass

            date = "Неизвестно"
            if change_file.exists():
                try:
                    with open(change_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'Дата обработки:' in line:
                                date_part = line.split('Дата обработки:')[1].strip()
                                date = date_part.split()[0]
                                break
                except:
                    pass

            if date == "Неизвестно":
                match = re.search(r'(\d{4})(\d{2})(\d{2})', training_id)
                if match:
                    year, month, day = match.groups()
                    date = f"{year}-{month}-{day}"

            date_obj = None
            if date != "Неизвестно":
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                except:
                    try:
                        date_obj = datetime.strptime(date, "%d.%m.%Y")
                    except:
                        date_obj = None

            if not date_obj:
                match = re.search(r'(\d{4})(\d{2})(\d{2})', training_id)
                if match:
                    year, month, day = match.groups()
                    try:
                        date_obj = datetime(int(year), int(month), int(day))
                        date = f"{year}-{month}-{day}"
                    except:
                        date_obj = datetime.min

            trainings.append({
                'id': training_id,
                'number': number,
                'title': f"Тренировка {number}",
                'date': date,
                'date_obj': date_obj,
                'tasks_count': tasks_count,
                'participants': participants,
                'max_points': max_points,
                'avg_points': avg_points,
                'monitor': monitor,
                'analysis': analysis,
                'video': video,
                'link': link,
                'tags': tags,
                'processed': processed
            })

    trainings.sort(key=lambda x: (
        int(x['number']) if x['number'].isdigit() else 0
    ), reverse=True)

    return trainings


def load_team_contests():
    contests = []
    team_contests_path = Path('team_contests')

    if not team_contests_path.exists():
        return contests

    contest_folders = list(team_contests_path.glob('contest_*'))

    for folder in contest_folders:
        if folder.is_dir():
            contest_id = folder.name

            number_match = re.search(r'contest_(\d+)', contest_id.lower())
            number = number_match.group(1).lstrip('0') if number_match else contest_id

            tags = []
            tags_file = folder / 'tags.txt'
            if tags_file.exists():
                try:
                    with open(tags_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        tags = [tag.strip() for tag in content.split(',') if tag.strip()]
                except:
                    pass

            monitor_file = folder / 'monitor.csv'
            change_file = folder / 'change.txt'
            analysis_files = list(folder.glob('*analysis*')) + list(folder.glob('*разбор*'))
            link_file = folder / 'link.txt'

            analysis = analysis_files[0].name if analysis_files else None
            processed_file = folder / 'processed.txt'
            processed = processed_file.exists()

            link = None
            if link_file.exists():
                try:
                    with open(link_file, 'r', encoding='utf-8') as f:
                        link = f.read().strip()
                except:
                    pass

            tasks_count = 0
            teams = 0

            if monitor_file.exists():
                try:
                    with open(monitor_file, 'r', encoding='utf-8') as f:
                        sample = f.read(1024)
                        f.seek(0)

                        if ';' in sample:
                            reader = csv.DictReader(f, delimiter=';')
                        else:
                            reader = csv.DictReader(f)

                        fieldnames = reader.fieldnames or []
                        exclude_fields = ['place', 'user_name', 'login', 'Участник', 'участник',
                                          'Score', 'score', 'Баллы', 'баллы', 'Penalty', 'penalty',
                                          'user', 'User', 'USER', 'фио', 'ФИО', 'Name', 'name']

                        for field in fieldnames:
                            if (field not in exclude_fields and
                                    not field.startswith('Unnamed:') and
                                    not re.match(r'^(фио|ФИО|user|name|имя|никнейм)', field.lower()) and
                                    field.strip() != ''):
                                tasks_count += 1

                        f.seek(0)
                        teams = sum(1 for _ in reader)
                except:
                    pass

            date = "Неизвестно"
            if processed_file.exists():
                try:
                    with open(processed_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'обработан:' in line:
                                date_part = line.split('обработан:')[1].strip()
                                date = date_part.split()[0]
                                break
                except:
                    pass

            if date == "Неизвестно":
                match = re.search(r'(\d{4})(\d{2})(\d{2})', contest_id)
                if match:
                    year, month, day = match.groups()
                    date = f"{year}-{month}-{day}"

            date_obj = None
            if date != "Неизвестно":
                try:
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                except:
                    try:
                        date_obj = datetime.strptime(date, "%d.%m.%Y")
                    except:
                        date_obj = None

            if not date_obj:
                match = re.search(r'(\d{4})(\d{2})(\d{2})', contest_id)
                if match:
                    year, month, day = match.groups()
                    try:
                        date_obj = datetime(int(year), int(month), int(day))
                        date = f"{year}-{month}-{day}"
                    except:
                        date_obj = datetime.min

            contests.append({
                'id': contest_id,
                'number': number,
                'title': f"Командный контест {number}",
                'date': date,
                'date_obj': date_obj,
                'tasks_count': tasks_count,
                'teams': teams,
                'analysis': analysis,
                'link': link,
                'tags': tags,
                'processed': processed
            })

    contests.sort(key=lambda x: (
        int(x['number']) if x['number'].isdigit() else 0
    ), reverse=True)

    return contests


def load_math_problems():
    math_problems = []
    math_path = Path('math')

    if not math_path.exists():
        return math_problems

    pdf_files = list(math_path.glob('*.pdf'))

    for pdf_file in pdf_files:
        if pdf_file.is_file():
            math_id = pdf_file.stem

            if '_solutions' in math_id:
                continue

            meta_file = math_path / f'{math_id}.txt'
            title = math_id
            author = "Неизвестно"
            date = "Неизвестно"
            description = ""
            tags = []
            pages = None
            solutions_filename = None

            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    lines = content.split('\n')
                    metadata = {}
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()

                    title = metadata.get('title', math_id)
                    author = metadata.get('author', 'Неизвестно')
                    date = metadata.get('date', 'Неизвестно')
                    description = metadata.get('description', '')
                    tags_str = metadata.get('tags', '')
                    if tags_str:
                        tags = [tag.strip() for tag in tags_str.split(',')]
                    pages_str = metadata.get('pages', '')
                    if pages_str and pages_str.isdigit():
                        pages = int(pages_str)
                    solutions_filename = metadata.get('solutions')
                except:
                    pass

            solutions_file = math_path / f'{math_id}_solutions.pdf'
            if not solutions_filename and solutions_file.exists():
                solutions_filename = solutions_file.name

            number_match = re.search(r'(\d+)', math_id)
            if number_match:
                number = str(int(number_match.group(1)))
            else:
                number = math_id

            math_problems.append({
                'id': math_id,
                'number': number,
                'title': title,
                'author': author,
                'date': date,
                'description': description,
                'tags': tags,
                'pages': pages,
                'filename': pdf_file.name,
                'solutions_filename': solutions_filename
            })

    def get_sort_key(math_problem):
        try:
            return int(math_problem['number'])
        except:
            try:
                return datetime.strptime(math_problem['date'], "%Y-%m-%d")
            except:
                return datetime.min

    math_problems.sort(key=get_sort_key, reverse=True)

    return math_problems


def load_news():
    news = []
    news_path = Path('news')

    news_files = list(news_path.glob('headline_*.txt'))

    for news_file in news_files:
        if news_file.is_file():
            news_id = news_file.stem

            number_match = re.search(r'headline_(\d+)', news_id.lower())
            number = number_match.group(1).lstrip('0') if number_match else news_id

            try:
                with open(news_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n', 5)
                metadata = {}
                for line in lines[:5]:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()

                title = metadata.get('title', 'Без названия')
                author = metadata.get('author', 'Неизвестно')
                date = metadata.get('date', 'Неизвестно')
                priority = metadata.get('priority', 'low')
                tags = metadata.get('tags', '').split(',') if metadata.get('tags') else []

                news_content = lines[5] if len(lines) > 5 else ""

                attachments = []
                attachment_files = list(news_file.parent.glob(f'{news_id}_*'))
                for att_file in attachment_files:
                    if att_file != news_file:
                        ext = att_file.suffix.lower()
                        icon = 'fa-file'
                        if ext in ['.pdf']:
                            icon = 'fa-file-pdf'
                        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                            icon = 'fa-file-image'
                        elif ext in ['.zip', '.rar']:
                            icon = 'fa-file-archive'
                        elif ext in ['.txt']:
                            icon = 'fa-file-alt'
                        elif ext in ['.xlsx', '.xls']:
                            icon = 'fa-file-excel'
                        elif ext in ['.doc', '.docx']:
                            icon = 'fa-file-word'

                        attachments.append({
                            'filename': att_file.name,
                            'name': att_file.stem,
                            'icon': icon,
                            'size': att_file.stat().st_size // 1024 if att_file.exists() else None
                        })

                news.append({
                    'id': news_id,
                    'number': number,
                    'title': title,
                    'author': author,
                    'date': date,
                    'priority': priority,
                    'tags': [tag.strip() for tag in tags],
                    'content': news_content,
                    'attachments': attachments,
                    'attachments_count': len(attachments)
                })
            except:
                continue

    news.sort(key=lambda x: (
        int(x['number']) if x['number'].isdigit() else 0
    ), reverse=True)

    return news


def get_participants():
    participants = []

    for nickname in rating_system.users.keys():
        stats = rating_system.get_user_stats(nickname)
        if stats:
            participants.append(stats)

    participants.sort(key=lambda x: x['rating'], reverse=True)

    return participants


def load_upcoming_contests():
    contests = load_contests()
    upcoming = []

    for contest in contests:
        if not contest['processed']:
            upcoming.append(contest)

    upcoming.sort(key=lambda x: int(x['number']) if x['number'].isdigit() else 0, reverse=True)

    return upcoming


@app.route('/')
def index():
    contests = load_contests()
    trainings = load_trainings()
    team_contests = load_team_contests()
    math_problems = load_math_problems()
    news = load_news()
    participants = get_participants()

    # Получаем ближайшие контесты
    upcoming_contests = load_upcoming_contests()

    total_contests = len(contests)
    total_trainings = len(trainings)
    total_team_contests = len(team_contests)
    total_math = len(math_problems)
    total_news = len(news)
    total_participants = len(participants)

    return render_template_string(
        HTML,
        contests=contests,
        trainings=trainings,
        team_contests=team_contests,
        math_problems=math_problems,
        news=news,
        participants=participants[:25],
        upcoming_contests=upcoming_contests,
        total_contests=total_contests,
        total_trainings=total_trainings,
        total_team_contests=total_team_contests,
        total_math=total_math,
        total_news=total_news,
        total_participants=total_participants
    )


@app.route('/contest/<contest_id>/<filename>')
def serve_contest_file(contest_id, filename):
    contest_path = Path('contests') / contest_id

    if not contest_path.exists() or not contest_path.is_dir():
        return "Контест не найден", 404

    file_path = contest_path / filename
    if not file_path.exists() or not file_path.is_file():
        return "Файл не найден", 404

    return send_from_directory(contest_path, filename)


@app.route('/training/<training_id>/<filename>')
def serve_training_file(training_id, filename):
    training_path = Path('trainings') / training_id

    if not training_path.exists() or not training_path.is_dir():
        return "Тренировка не найден", 404

    file_path = training_path / filename
    if not file_path.exists() or not file_path.is_file():
        return "Файл не найден", 404

    return send_from_directory(training_path, filename)


@app.route('/team_contest/<contest_id>/<filename>')
def serve_team_contest_file(contest_id, filename):
    contest_path = Path('team_contests') / contest_id

    if not contest_path.exists() or not contest_path.is_dir():
        return "Командный контест не найден", 404

    file_path = contest_path / filename
    if not file_path.exists() or not file_path.is_file():
        return "Файл не найден", 404

    return send_from_directory(contest_path, filename)


@app.route('/news/<news_id>/<filename>')
def serve_news_file(news_id, filename):
    news_path = Path('news')

    file_path = news_path / filename
    if not file_path.exists() or not file_path.is_file():
        return "Файл не найден", 404

    return send_from_directory(news_path, filename)


@app.route('/api/user/<nickname>/chart')
def get_user_chart(nickname):
    chart_data = rating_system.generate_rating_chart(nickname)

    if chart_data:
        return f'<img src="data:image/png;base64,{chart_data}" alt="Rating Chart" style="max-width:100%;">'
    else:
        return '<p>Недостаточно данных для построения графика. Нужно минимум 2 контеста.</p>'


@app.route('/api/user/<nickname>/details')
def get_user_details(nickname):
    stats = rating_system.get_user_stats(nickname)

    if stats:
        return jsonify({
            'success': True,
            'user': stats
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Пользователь не найден'
        })


@app.route('/api/contest/<contest_id>')
def get_contest_details(contest_id):
    division = request.args.get('division', '1')
    try:
        division = int(division)
    except:
        division = 1

    contest_path = Path('contests') / contest_id

    if not contest_path.exists():
        return jsonify({'success': False, 'error': 'Контест не найден'})

    division_dir = contest_path / f'div{division}'
    change_file = division_dir / 'change.txt'
    processed = change_file.exists()

    tags = []
    tags_file = contest_path / 'tags.txt'
    if tags_file.exists():
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                tags = [tag.strip() for tag in content.split(',') if tag.strip()]
        except:
            pass

    results = []
    monitor_file = division_dir / 'monitor.csv'

    if processed and change_file.exists():
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            start_line = 0
            for i, line in enumerate(lines):
                if '=====' in line:
                    start_line = i + 1
                    break

            for line in lines[start_line:]:
                line = line.strip()
                if not line:
                    continue

                match = re.match(
                    r'(\d+)\.\s+([^:]+):\s+(\d+)\s+\([^)]+\)\s+→\s+(\d+)\s+\([^)]+\)\s+\(([+-]\d+)\)',
                    line)
                if match:
                    nickname = match.group(2).strip()
                    old_rating = int(match.group(3))
                    new_rating = int(match.group(4))
                    change = int(match.group(5))

                    unofficial = "[UNR]" in line

                    score = "0"
                    if monitor_file.exists():
                        try:
                            with open(monitor_file, 'r', encoding='utf-8') as mf:
                                sample = mf.read(1024)
                                mf.seek(0)

                                if ';' in sample:
                                    reader = csv.DictReader(mf, delimiter=';')
                                else:
                                    reader = csv.DictReader(mf)

                                for row in reader:
                                    row_nickname = row.get('user_name', '') or row.get('login', '')
                                    if row_nickname.strip() == nickname:
                                        score = row.get('Score', '0').strip()
                                        break
                        except:
                            pass

                    results.append({
                        'nickname': nickname,
                        'score': score,
                        'rating': new_rating,
                        'change': change,
                        'unofficial': unofficial
                    })
        except:
            pass

    tasks_count = 0
    if monitor_file.exists():
        try:
            with open(monitor_file, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)

                if ';' in sample:
                    reader = csv.DictReader(f, delimiter=';')
                else:
                    reader = csv.DictReader(f)

                fieldnames = reader.fieldnames or []
                exclude_fields = ['place', 'user_name', 'login', 'Участник', 'участник',
                                  'Score', 'Penalty', 'score', 'penalty', 'Баллы', 'баллы',
                                  'user', 'User', 'USER', 'фио', 'ФИО']

                for field in fieldnames:
                    if (field not in exclude_fields and
                            not field.startswith('Unnamed:') and
                            not re.match(r'^(фио|ФИО|user|name|имя|никнейм)', field.lower()) and
                            field.strip() != ''):
                        tasks_count += 1
        except:
            pass

    divisions = []
    total_participants = 0

    for div_num in [1, 2, 3, 4]:
        div_dir = contest_path / f'div{div_num}'
        if div_dir.exists():
            link_file = div_dir / 'link.txt'
            div_monitor = div_dir / 'monitor.csv'
            div_change = div_dir / 'change.txt'

            link = ""
            if link_file.exists():
                try:
                    with open(link_file, 'r', encoding='utf-8') as f:
                        link = f.read().strip()
                except:
                    pass

            participants = 0
            if div_change.exists():
                try:
                    with open(div_change, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'Участников официально:' in line:
                                parts = line.split(':')
                                if len(parts) > 1:
                                    try:
                                        participants = int(parts[1].strip())
                                        total_participants += participants
                                    except:
                                        pass
                                break
                except:
                    pass

            divisions.append({
                'division': div_num,
                'link': link,
                'color': DivisionSystem.DIVISION_COLORS[div_num],
                'participants': participants,
                'processed': div_change.exists(),
                'has_monitor': div_monitor.exists()
            })

    analysis = None
    analysis_files = list(contest_path.glob('*analysis*')) + list(contest_path.glob('*разбор*'))
    if analysis_files:
        analysis = analysis_files[0].name

    date = "Неизвестно"
    winner = ""
    max_rating = 0

    if processed and change_file.exists():
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if 'Дата обработки:' in line:
                        date_part = line.split('Дата обработки:')[1].strip()
                        date = date_part.split()[0]
                    elif line.strip().startswith('1.'):
                        winner_match = re.match(r'1\.\s+([^:]+):', line)
                        if winner_match:
                            winner = winner_match.group(1).strip()
        except:
            pass

    return jsonify({
        'success': True,
        'contest': {
            'id': contest_id,
            'title': f"Контест {contest_id.replace('contest_', '')}",
            'results': results,
            'tasks_count': tasks_count,
            'total_participants': total_participants,
            'date': date,
            'winner': winner,
            'max_rating': max_rating,
            'divisions': divisions,
            'analysis': analysis,
            'has_monitor': monitor_file.exists(),
            'processed': processed,
            'division': division,
            'tags': tags
        }
    })


@app.route('/api/training/<training_id>')
def get_training_details(training_id):
    training_path = Path('trainings') / training_id

    if not training_path.exists():
        return jsonify({'success': False, 'error': 'Тренировка не найдена'})

    change_file = training_path / 'change.txt'
    processed = change_file.exists()

    tags = []
    tags_file = training_path / 'tags.txt'
    if tags_file.exists():
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                tags = [tag.strip() for tag in content.split(',') if tag.strip()]
        except:
            pass

    results = []

    if processed and change_file.exists():
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            start_line = 0
            for i, line in enumerate(lines):
                if '=====' in line:
                    start_line = i + 1
                    break

            for line in lines[start_line:]:
                line = line.strip()
                if not line:
                    continue

                match = re.match(r'(\d+)\.\s+([^:]+):\s+решено\s+(\d+)\s+задач', line)
                if match:
                    nickname = match.group(2).strip()
                    solved = int(match.group(3))

                    results.append({
                        'nickname': nickname,
                        'solved': solved,
                        'points': solved,
                    })
        except:
            pass

    monitor_file = training_path / 'monitor.csv'

    tasks_count = 0
    if monitor_file.exists():
        try:
            with open(monitor_file, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)

                if ';' in sample:
                    reader = csv.DictReader(f, delimiter=';')
                else:
                    reader = csv.DictReader(f)

                fieldnames = reader.fieldnames or []
                exclude_fields = ['place', 'user_name', 'login', 'user', 'User', 'USER',
                                  'Score', 'Penalty', 'score', 'penalty', 'фио', 'ФИО']

                for field in fieldnames:
                    if (field not in exclude_fields and
                            not field.startswith('Unnamed:') and
                            not re.match(r'^(фио|ФИО|user|name|имя|никнейм)', field.lower()) and
                            field.strip() != ''):
                        tasks_count += 1
        except:
            pass

    analysis_files = list(training_path.glob('*analysis*')) + list(training_path.glob('*разбор*'))
    video_file = training_path / 'video.txt'
    link_file = training_path / 'link.txt'

    analysis = analysis_files[0].name if analysis_files else None
    monitor = monitor_file.name if monitor_file.exists() else None

    video = None
    if video_file.exists():
        try:
            with open(video_file, 'r', encoding='utf-8') as f:
                video = f.read().strip()
        except:
            pass

    link = None
    if link_file.exists():
        try:
            with open(link_file, 'r', encoding='utf-8') as f:
                link = f.read().strip()
        except:
            pass

    date = "Неизвестно"
    if change_file.exists():
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Дата обработки:' in line:
                        date_part = line.split('Дата обработки:')[1].strip()
                        date = date_part.split()[0]
                        break
        except:
            pass

    participants = len(results)

    return jsonify({
        'success': True,
        'training': {
            'id': training_id,
            'title': f"Тренировка {training_id.replace('training_', '')}",
            'results': results,
            'tasks_count': tasks_count,
            'participants': participants,
            'date': date,
            'analysis': analysis,
            'monitor': monitor,
            'video': video,
            'link': link,
            'processed': processed,
            'tags': tags
        }
    })


@app.route('/api/team_contest/<contest_id>')
def get_team_contest_details(contest_id):
    contest_path = Path('team_contests') / contest_id

    if not contest_path.exists():
        return jsonify({'success': False, 'error': 'Командный контест не найден'})

    change_file = contest_path / 'change.txt'
    processed = change_file.exists()

    tags = []
    tags_file = contest_path / 'tags.txt'
    if tags_file.exists():
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                tags = [tag.strip() for tag in content.split(',') if tag.strip()]
        except:
            pass

    results = []
    monitor_file = contest_path / 'monitor.csv'

    if processed and change_file.exists():
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            start_line = 0
            for i, line in enumerate(lines):
                if '=====' in line:
                    start_line = i + 1
                    break

            for line in lines[start_line:]:
                line = line.strip()
                if not line:
                    continue

                match = re.match(r'(\d+)\.\s+([^:]+):\s+(\d+)\s+баллов', line)
                if match:
                    team_name = match.group(2).strip()
                    score = int(match.group(3))

                    members = []
                    if '(' in line and ')' in line:
                        members_part = line[line.find('(') + 1:line.find(')')]
                        if 'Участники:' in members_part:
                            members = [m.strip() for m in members_part.split('Участники:')[1].split(',')]
                        else:
                            members = [m.strip() for m in members_part.split(',')]

                    results.append({
                        'team_name': team_name,
                        'score': score,
                        'members': members,
                        'member_count': len(members)
                    })
        except:
            pass

    tasks_count = 0
    teams = 0

    if monitor_file.exists():
        try:
            with open(monitor_file, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)

                if ';' in sample:
                    reader = csv.DictReader(f, delimiter=';')
                else:
                    reader = csv.DictReader(f)

                fieldnames = reader.fieldnames or []
                exclude_fields = ['place', 'team_name', 'Team', 'Команда', 'team',
                                  'Score', 'score', 'Баллы', 'баллы', 'Penalty', 'penalty',
                                  'members', 'Участники', 'участники']

                for field in fieldnames:
                    if (field not in exclude_fields and
                            not field.startswith('Unnamed:') and
                            field.strip() != ''):
                        tasks_count += 1

                f.seek(0)
                teams = sum(1 for _ in reader)
        except:
            pass

    analysis = None
    analysis_files = list(contest_path.glob('*analysis*')) + list(contest_path.glob('*разбор*'))
    if analysis_files:
        analysis = analysis_files[0].name

    link = None
    link_file = contest_path / 'link.txt'
    if link_file.exists():
        try:
            with open(link_file, 'r', encoding='utf-8') as f:
                link = f.read().strip()
        except:
            pass

    date = "Неизвестно"
    if change_file.exists():
        try:
            with open(change_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Дата обработки:' in line:
                        date_part = line.split('Дата обработки:')[1].strip()
                        date = date_part.split()[0]
                        break
        except:
            pass

    return jsonify({
        'success': True,
        'contest': {
            'id': contest_id,
            'title': f"Командный контест {contest_id.replace('contest_', '')}",
            'results': results,
            'tasks_count': tasks_count,
            'teams': teams,
            'date': date,
            'analysis': analysis,
            'link': link,
            'processed': processed,
            'tags': tags
        }
    })


@app.route('/api/news/<news_id>')
def get_news_details(news_id):
    news_path = Path('news')
    news_file = news_path / f'{news_id}.txt'

    if not news_file.exists():
        return jsonify({'success': False, 'error': 'Новость не найдена'})

    try:
        with open(news_file, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n', 5)
        metadata = {}
        for line in lines[:5]:
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()

        title = metadata.get('title', 'Без названия')
        author = metadata.get('author', 'Неизвестно')
        date = metadata.get('date', 'Неизвестно')
        priority = metadata.get('priority', 'low')
        tags = metadata.get('tags', '').split(',') if metadata.get('tags') else []

        news_content = lines[5] if len(lines) > 5 else ""

        attachments = []
        attachment_files = list(news_file.parent.glob(f'{news_id}_*'))
        for att_file in attachment_files:
            if att_file != news_file:
                ext = att_file.suffix.lower()
                icon = 'fa-file'
                if ext in ['.pdf']:
                    icon = 'fa-file-pdf'
                elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    icon = 'fa-file-image'
                elif ext in ['.zip', '.rar']:
                    icon = 'fa-file-archive'
                elif ext in ['.txt']:
                    icon = 'fa-file-alt'
                elif ext in ['.xlsx', '.xls']:
                    icon = 'fa-file-excel'
                elif ext in ['.doc', '.docx']:
                    icon = 'fa-file-word'

                attachments.append({
                    'filename': att_file.name,
                    'name': att_file.stem,
                    'icon': icon,
                    'size': att_file.stat().st_size // 1024 if att_file.exists() else None
                })

        number_match = re.search(r'headline_(\d+)', news_id.lower())
        number = number_match.group(1).lstrip('0') if number_match else news_id

        return jsonify({
            'success': True,
            'news': {
                'id': news_id,
                'number': number,
                'title': title,
                'author': author,
                'date': date,
                'priority': priority,
                'tags': [tag.strip() for tag in tags],
                'content': news_content,
                'attachments': attachments,
                'attachments_count': len(attachments)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка чтения новости: {str(e)}'
        })


@app.route('/api/news/<news_id>/attachments')
def get_news_attachments(news_id):
    news_path = Path('news')
    attachments = []

    try:
        attachment_files = list(news_path.glob(f'{news_id}_*'))
        for att_file in attachment_files:
            if att_file.is_file():
                ext = att_file.suffix.lower()
                icon = 'fa-file'
                if ext in ['.pdf']:
                    icon = 'fa-file-pdf'
                elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    icon = 'fa-file-image'
                elif ext in ['.zip', '.rar']:
                    icon = 'fa-file-archive'
                elif ext in ['.txt']:
                    icon = 'fa-file-alt'
                elif ext in ['.xlsx', '.xls']:
                    icon = 'fa-file-excel'
                elif ext in ['.doc', '.docx']:
                    icon = 'fa-file-word'

                attachments.append({
                    'filename': att_file.name,
                    'name': att_file.stem,
                    'icon': icon,
                    'size': att_file.stat().st_size // 1024 if att_file.exists() else None
                })

        return jsonify({
            'success': True,
            'attachments': attachments
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка получения вложений: {str(e)}'
        })


@app.route('/api/contest/<contest_id>/monitor')
def get_contest_monitor(contest_id):
    division = request.args.get('division', '1')
    try:
        division = int(division)
    except:
        division = 1

    contest_path = Path('contests') / contest_id

    if not contest_path.exists():
        return jsonify({'success': False, 'error': 'Контест не найден'})

    division_dir = contest_path / f'div{division}'
    monitor_file = division_dir / 'monitor.csv'
    change_file = division_dir / 'change.txt'

    if not monitor_file.exists():
        return jsonify({'success': False, 'error': 'Монитор не найден'})

    try:
        participants = []
        task_names = []
        stats = {
            'total_participants': 0,
            'official_participants': 0,
            'unofficial_participants': 0,
            'tasks_count': 0,
            'max_score': 0,
            'avg_score': 0
        }

        # Сначала пытаемся загрузить из change.txt (замороженные результаты)
        if change_file.exists():
            participants_from_change = []
            try:
                with open(change_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                start_line = 0
                for i, line in enumerate(lines):
                    if '=====' in line:
                        start_line = i + 1
                        break

                for line in lines[start_line:]:
                    line = line.strip()
                    if not line:
                        continue

                    # Определяем unofficial статус
                    unofficial = "[UNR]" in line or "UNRATED" in line

                    # Убираем маркеры unofficial из строки для парсинга
                    clean_line = line.replace('[UNR]', '').replace('UNRATED', '').strip()

                    # Парсим строку
                    match = re.match(
                        r'(\d+)\.\s+([^:]+):\s+(\d+)\s+\([^)]+\)\s+→\s+(\d+)\s+\([^)]+\)\s+\(([+-]\d+)\)',
                        clean_line)
                    if match:
                        nickname = match.group(2).strip()
                        old_rating = int(match.group(3))
                        new_rating = int(match.group(4))
                        change = int(match.group(5))

                        # Извлекаем количество решенных задач если есть
                        tasks_solved_match = re.search(r'задач:\s+(\d+)', clean_line)
                        tasks_solved = int(tasks_solved_match.group(1)) if tasks_solved_match else 0

                        # Извлекаем allowed_division если есть
                        allowed_division_match = re.search(r'allowed_div:(\d+)', line)
                        allowed_division = int(allowed_division_match.group(1)) if allowed_division_match else division

                        # Берем данные из монитора для тасков
                        tasks = []
                        if monitor_file.exists():
                            try:
                                with open(monitor_file, 'r', encoding='utf-8') as mf:
                                    sample = mf.read(1024)
                                    mf.seek(0)

                                    if ';' in sample:
                                        reader = csv.DictReader(mf, delimiter=';')
                                    else:
                                        reader = csv.DictReader(mf)

                                    fieldnames = reader.fieldnames or []
                                    exclude_fields = ['place', 'user_name', 'login', 'Участник', 'участник',
                                                      'Score', 'score', 'Баллы', 'баллы', 'Penalty', 'penalty',
                                                      'user', 'User', 'USER', 'фио', 'ФИО', 'Name', 'name', 'никнейм',
                                                      'Имя', 'имя', 'Nickname', 'nickname']

                                    task_names = [field for field in fieldnames
                                                  if field not in exclude_fields
                                                  and not field.startswith('Unnamed:')
                                                  and not re.match(r'^(фио|ФИО|user|name|имя|никнейм)', field.lower())
                                                  and field.strip() != '']

                                    for row in reader:
                                        row_nickname = row.get('user_name', '') or row.get('login', '') or row.get(
                                            'Участник', '')
                                        if row_nickname.strip() == nickname:
                                            for task_name in task_names:
                                                task_value = row.get(task_name, '').strip()
                                                status = 'pending'
                                                display = task_value

                                                if task_value:
                                                    if '+' in task_value:
                                                        status = 'solved'
                                                        display = '+' + task_value.replace('+', '')
                                                    elif task_value.isdigit() and int(task_value) > 0:
                                                        status = 'solved'
                                                        display = task_value
                                                    elif '-' in task_value:
                                                        status = 'attempted'
                                                        display = '-' + task_value.replace('-', '')

                                                tasks.append({
                                                    'name': task_name,
                                                    'value': task_value,
                                                    'status': status,
                                                    'display': display
                                                })
                                            break
                            except:
                                pass

                        participants_from_change.append({
                            'nickname': nickname,
                            'rating': new_rating,
                            'change': change,
                            'unofficial': unofficial,
                            'tasks': tasks,
                            'tasks_solved': tasks_solved,
                            'allowed_division': allowed_division
                        })

                        if unofficial:
                            stats['unofficial_participants'] += 1
                        else:
                            stats['official_participants'] += 1
                            stats['total_participants'] += 1

            except Exception as e:
                print(f"Ошибка чтения change.txt: {e}")

            # Сортируем участников по их позиции в change.txt
            if participants_from_change:
                participants = participants_from_change
                stats['tasks_count'] = len(task_names) if task_names else 0

                # Рассчитываем средний балл
                scores = []
                for p in participants:
                    if not p['unofficial']:
                        score = 0
                        for task in p['tasks']:
                            if task['status'] == 'solved':
                                score += 1
                        scores.append(score)

                if scores:
                    stats['max_score'] = max(scores)
                    stats['avg_score'] = sum(scores) / len(scores)

        # Если нет change.txt, загружаем из monitor.csv
        else:
            with open(monitor_file, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)

                if ';' in sample:
                    reader = csv.DictReader(f, delimiter=';')
                else:
                    reader = csv.DictReader(f)

                fieldnames = reader.fieldnames or []

                exclude_fields = ['place', 'user_name', 'login', 'Участник', 'участник',
                                  'Score', 'score', 'Баллы', 'баллы', 'Penalty', 'penalty',
                                  'user', 'User', 'USER', 'фио', 'ФИО', 'Name', 'name', 'никнейм',
                                  'Имя', 'имя', 'Nickname', 'nickname']

                task_names = [field for field in fieldnames
                              if field not in exclude_fields
                              and not field.startswith('Unnamed:')
                              and not re.match(r'^(фий|ФИО|user|name|имя|никнейм)', field.lower())
                              and field.strip() != '']

                stats['tasks_count'] = len(task_names)

                for i, row in enumerate(reader):
                    nickname = row.get('user_name', '') or row.get('login', '') or row.get('Участник', '')
                    if nickname and nickname.strip():
                        nickname = nickname.strip()

                        score_str = row.get('Score', '0') or row.get('score', '0') or row.get('Баллы', '0')
                        try:
                            score = float(score_str)
                        except:
                            score = 0

                        # Определяем unofficial на основе строгого правила
                        user_ratings = rating_system.users.get(nickname, {1: 0, 2: 0, 3: 0, 4: 0})

                        # НАХОДИМ МАКСИМАЛЬНЫЙ РЕЙТИНГ пользователя
                        max_rating = 0
                        for div in [1, 2, 3, 4]:
                            rating = user_ratings.get(div, 0)
                            if rating > max_rating:
                                max_rating = rating

                        # СТРОГОЕ ПРАВИЛО: определяем разрешенный дивизион по максимальному рейтингу
                        allowed_division = None

                        if max_rating == 0:
                            # Новичок без рейтинга - только Div4
                            allowed_division = 4
                        elif 0 <= max_rating <= 999:
                            allowed_division = 4
                        elif 1000 <= max_rating <= 1999:
                            allowed_division = 3
                        elif 2000 <= max_rating <= 2999:
                            allowed_division = 2
                        elif 3000 <= max_rating <= 4000:
                            allowed_division = 1
                        else:
                            # Если рейтинг выше 4000 - Div1
                            allowed_division = 1

                        # Определяем unofficial статус
                        # Участник официальный ТОЛЬКО если пишет в своем allowed_division
                        unofficial = (division != allowed_division)

                        # Для отладки
                        if max_rating >= 1000 and division == 4:
                            print(
                                f"СТРОГОЕ ПРАВИЛО: {nickname} rating={max_rating}, allowed_div={allowed_division}, current_div={division}, unofficial={unofficial}")

                        tasks = []
                        for task_name in task_names:
                            task_value = row.get(task_name, '').strip()
                            status = 'pending'
                            display = task_value

                            if task_value:
                                if '+' in task_value:
                                    status = 'solved'
                                    display = '+' + task_value.replace('+', '')
                                elif task_value.isdigit() and int(task_value) > 0:
                                    status = 'solved'
                                    display = task_value
                                elif '-' in task_value:
                                    status = 'attempted'
                                    display = '-' + task_value.replace('-', '')

                            tasks.append({
                                'name': task_name,
                                'value': task_value,
                                'status': status,
                                'display': display
                            })

                        current_rating = user_ratings.get(division, 0)

                        participants.append({
                            'nickname': nickname,
                            'score': score,
                            'rating': current_rating,
                            'unofficial': unofficial,
                            'tasks': tasks,
                            'position': i + 1,
                            'allowed_division': allowed_division,
                            'max_rating': max_rating
                        })

                        if unofficial:
                            stats['unofficial_participants'] += 1
                        else:
                            stats['total_participants'] += 1
                            stats['official_participants'] += 1

                        if score > stats['max_score']:
                            stats['max_score'] = score

            # Сортируем только официальных участников
            official_participants = [p for p in participants if not p['unofficial']]
            official_participants.sort(key=lambda x: x['score'], reverse=True)

            # Обновляем позиции
            for i, participant in enumerate(official_participants):
                participant['position'] = i + 1

            if official_participants:
                stats['avg_score'] = sum(p['score'] for p in official_participants) / len(official_participants)

        # Получаем информацию о других дивизионах
        divisions = []
        for div_num in [1, 2, 3, 4]:
            div_dir = contest_path / f'div{div_num}'
            if div_dir.exists():
                div_monitor = div_dir / 'monitor.csv'
                if div_monitor.exists():
                    participants_count = 0
                    try:
                        with open(div_monitor, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            participants_count = sum(1 for _ in reader)
                    except:
                        pass

                    divisions.append({
                        'division': div_num,
                        'color': DivisionSystem.DIVISION_COLORS[div_num],
                        'participants': participants_count,
                        'has_monitor': True
                    })

        # Получаем дату контеста
        date = "Неизвестно"
        if change_file.exists():
            try:
                with open(change_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'Дата обработки:' in line:
                            date_part = line.split('Дата обработки:')[1].strip()
                            date = date_part.split()[0]
                            break
            except:
                pass

        return jsonify({
            'success': True,
            'monitor': {
                'contest_id': contest_id,
                'current_division': division,
                'participants': [p for p in participants if not p['unofficial']],  # Только официальные
                'task_names': task_names,
                'stats': stats,
                'divisions': divisions,
                'date': date,
                'tasks_count': stats['tasks_count'],
                'total_participants': stats['total_participants'],
                'show_only_official': True,
                'unofficial_count': stats['unofficial_participants'],
                'processed': change_file.exists()
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': f'Ошибка чтения монитора: {str(e)}\n{traceback.format_exc()}'
        })


@app.route('/api/team_contest/<contest_id>/monitor')
def get_team_contest_monitor(contest_id):
    contest_path = Path('team_contests') / contest_id

    if not contest_path.exists():
        return jsonify({'success': False, 'error': 'Командный контест не найден'})

    monitor_file = contest_path / 'monitor.csv'
    change_file = contest_path / 'change.txt'

    if not monitor_file.exists():
        return jsonify({'success': False, 'error': 'Монитор не найден'})

    try:
        teams = []
        task_names = []
        stats = {
            'total_teams': 0,
            'tasks_count': 0,
            'max_score': 0,
            'avg_score': 0,
            'members_per_team': 1
        }

        with open(monitor_file, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)

            if ';' in sample:
                reader = csv.DictReader(f, delimiter=';')
            else:
                reader = csv.DictReader(f)

            fieldnames = reader.fieldnames or []

            team_name_field = None
            possible_fields = ['user_name', 'login', 'Участник', 'участник', 'team_name', 'Team', 'Команда',
                               'team', 'Name', 'name', 'Имя', 'имя', 'ФИО', 'фио', 'user', 'User']

            for field in possible_fields:
                if field in fieldnames:
                    team_name_field = field
                    break

            if not team_name_field and fieldnames:
                exclude_first = ['place', 'место', 'Place']
                for field in fieldnames:
                    if field not in exclude_first:
                        team_name_field = field
                        break

            score_field = None
            possible_score_fields = ['Score', 'score', 'Баллы', 'баллы', 'points', 'Points']
            for field in possible_score_fields:
                if field in fieldnames:
                    score_field = field
                    break

            exclude_fields = ['place', 'user_name', 'login', 'Участник', 'участник',
                              'Score', 'score', 'Баллы', 'баллы', 'Penalty', 'penalty',
                              'user', 'User', 'USER', 'фио', 'ФИО', 'Name', 'name',
                              'никнейм', 'Имя', 'имя', 'Nickname', 'nickname', 'team_name',
                              'Team', 'Команда', 'team']

            if team_name_field and team_name_field not in exclude_fields:
                exclude_fields.append(team_name_field)
            if score_field and score_field not in exclude_fields:
                exclude_fields.append(score_field)

            task_names = [field for field in fieldnames
                          if field not in exclude_fields
                          and not field.startswith('Unnamed:')
                          and field.strip() != '']

            stats['tasks_count'] = len(task_names)

            for i, row in enumerate(reader):
                if team_name_field and team_name_field in row:
                    team_name = row[team_name_field]
                    if team_name and str(team_name).strip():
                        team_name = str(team_name).strip()

                        score = 0
                        if score_field and score_field in row:
                            try:
                                score = float(str(row[score_field]))
                            except:
                                pass
                        else:
                            for task_name in task_names:
                                if task_name in row:
                                    task_value = str(row[task_name]).strip()
                                    if task_value and ('+' in task_value or task_value.isdigit()):
                                        try:
                                            if '+' in task_value:
                                                num = task_value.replace('+', '').strip()
                                                if num.isdigit():
                                                    score += int(num)
                                                else:
                                                    score += 1
                                            else:
                                                score += int(task_value)
                                        except:
                                            score += 1

                        members = [team_name]

                        tasks = []
                        for task_name in task_names:
                            task_value = row.get(task_name, '').strip()
                            status = 'pending'
                            display = task_value

                            if task_value:
                                if '+' in task_value:
                                    status = 'solved'
                                    display = '+' + task_value.replace('+', '')
                                elif task_value.isdigit() and int(task_value) > 0:
                                    status = 'solved'
                                    display = task_value
                                elif '-' in task_value:
                                    status = 'attempted'
                                    display = '-' + task_value.replace('-', '')

                            tasks.append({
                                'name': task_name,
                                'value': task_value,
                                'status': status,
                                'display': display
                            })

                        teams.append({
                            'team_name': team_name,
                            'score': score,
                            'members': members,
                            'member_count': 1,
                            'tasks': tasks,
                            'position': i + 1
                        })

                        stats['total_teams'] += 1
                        if score > stats['max_score']:
                            stats['max_score'] = score

        teams.sort(key=lambda x: x['score'], reverse=True)

        if teams:
            stats['avg_score'] = sum(t['score'] for t in teams) / len(teams)

        date = "Неизвестно"
        if change_file.exists():
            try:
                with open(change_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'Дата обработки:' in line:
                            date_part = line.split('Дата обработки:')[1].strip()
                            date = date_part.split()[0]
                            break
            except:
                pass

        return jsonify({
            'success': True,
            'monitor': {
                'contest_id': contest_id,
                'teams': teams,
                'task_names': task_names,
                'stats': stats,
                'date': date,
                'tasks_count': stats['tasks_count'],
                'total_teams': stats['total_teams']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка чтения монитора: {str(e)}'
        })


@app.route('/api/contest/<contest_id>/monitor/download')
def download_contest_monitor(contest_id):
    division = request.args.get('division', '1')
    try:
        division = int(division)
    except:
        division = 1

    contest_path = Path('contests') / contest_id
    division_dir = contest_path / f'div{division}'
    monitor_file = division_dir / 'monitor.csv'

    if not monitor_file.exists():
        return "Файл не найден", 404

    return send_from_directory(division_dir, 'monitor.csv', as_attachment=True)


@app.route('/api/training/<training_id>/monitor/download')
def download_training_monitor(training_id):
    training_path = Path('trainings') / training_id
    monitor_file = training_path / 'monitor.csv'

    if not monitor_file.exists():
        return "Файл не найден", 404

    return send_from_directory(training_path, 'monitor.csv', as_attachment=True)


@app.route('/api/team_contest/<contest_id>/monitor/download')
def download_team_contest_monitor(contest_id):
    contest_path = Path('team_contests') / contest_id
    monitor_file = contest_path / 'monitor.csv'

    if not monitor_file.exists():
        return "Файл не найден", 404

    return send_from_directory(contest_path, 'monitor.csv', as_attachment=True)


@app.route('/api/contest/<contest_id>/process', methods=['POST'])
def process_contest_division(contest_id):
    data = request.get_json() or {}
    division = data.get('division', 1)

    try:
        division = int(division)
    except:
        division = 1

    success, message = rating_system.process_division(contest_id, division)

    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        })


@app.route('/api/contest/<contest_id>/process-all', methods=['POST'])
def process_all_divisions(contest_id):
    success, message = rating_system.process_all_divisions(contest_id)

    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        })


@app.route('/api/training/<training_id>/process', methods=['POST'])
def process_training_route(training_id):
    success, message = rating_system.process_training(training_id)

    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        })


@app.route('/api/team_contest/<contest_id>/process', methods=['POST'])
def process_team_contest_route(contest_id):
    success, message = rating_system.process_team_contest(contest_id)

    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        })


@app.route('/api/users')
def api_users():
    participants = get_participants()
    return jsonify({
        'success': True,
        'count': len(participants),
        'users': participants
    })


@app.route('/math/<math_id>/<filename>')
def serve_math_file(math_id, filename):
    math_path = Path('math')

    file_path = math_path / filename
    if not file_path.exists() or not file_path.is_file():
        return "Файл не найден", 404

    return send_from_directory(math_path, filename)


@app.route('/api/math/<math_id>')
def get_math_details(math_id):
    math_path = Path('math')

    pdf_file = math_path / f'{math_id}.pdf'
    if not pdf_file.exists():
        pdf_files = list(math_path.glob(f'{math_id}*.pdf'))
        if not pdf_files:
            return jsonify({'success': False, 'error': 'Математический материал не найден'})
        pdf_file = pdf_files[0]

    meta_file = math_path / f'{math_id}.txt'
    title = math_id
    author = "Неизвестно"
    date = "Неизвестно"
    description = ""
    tags = []
    pages = None
    solutions_filename = None

    if meta_file.exists():
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            metadata = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            title = metadata.get('title', math_id)
            author = metadata.get('author', 'Неизвестно')
            date = metadata.get('date', 'Неизвестно')
            description = metadata.get('description', '')
            tags_str = metadata.get('tags', '')
            if tags_str:
                tags = [tag.strip() for tag in tags_str.split(',')]
            pages_str = metadata.get('pages', '')
            if pages_str and pages_str.isdigit():
                pages = int(pages_str)
            solutions_filename = metadata.get('solutions')
        except:
            pass

    solutions_file = math_path / f'{math_id}_solutions.pdf'
    if not solutions_filename and solutions_file.exists():
        solutions_filename = solutions_file.name

    number_match = re.search(r'(\d+)', math_id)
    number = number_match.group(1) if number_match else math_id

    return jsonify({
        'success': True,
        'math': {
            'id': math_id,
            'number': number,
            'title': title,
            'author': author,
            'date': date,
            'description': description,
            'tags': tags,
            'pages': pages,
            'filename': pdf_file.name,
            'solutions_filename': solutions_filename
        }
    })


@app.route('/users')
def users_page():
    participants = get_participants()

    html = '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Все участники</title>
        <style>
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                background: #f0f0f0;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .back-btn {
                padding: 10px 20px;
                background: #3b5998;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
            }
            .user-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }
            .user-card {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #e0e0e0;
                transition: all 0.3s;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }
            .user-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                border-color: #1a73e8;
            }
            .user-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 5px;
                background: linear-gradient(90deg, #667eea, #764ba2);
            }
            .user-rank {
                position: absolute;
                top: 10px;
                right: 10px;
                background: #3b5998;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }
            .user-avatar {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                font-weight: bold;
                color: white;
                margin-bottom: 15px;
            }
            .user-name {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 5px;
                color: #333;
            }
            .user-rating {
                font-size: 28px;
                font-weight: bold;
                margin: 10px 0;
            }
            .user-tasks-score {
                font-size: 20px;
                font-weight: bold;
                color: #4CAF50;
                margin: 5px 0;
            }
            .user-stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                font-size: 14px;
                color: #666;
            }
            .stat-item {
                background: white;
                padding: 8px;
                border-radius: 5px;
                text-align: center;
            }
            .search-box {
                margin-bottom: 20px;
            }
            .search-input {
                width: 100%;
                padding: 12px 15px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
            }
            .contact-info {
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                font-size: 14px;
                color: #666;
            }
            .contact-info a {
                color: #1a73e8;
                text-decoration: none;
                margin: 0 10px;
            }
            .contact-info a:hover {
                text-decoration: underline;
            }
            @media (max-width: 768px) {
                .user-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>
                <span>Все участники (''' + str(len(participants)) + ''')</span>
                <a href="/" class="back-btn">← Назад к дашборду</a>
            </h1>

            <div class="search-box">
                <input type="text" 
                       class="search-input" 
                       placeholder="🔍 Поиск участника..."
                       id="searchInput"
                       onkeyup="filterUsers()">
            </div>

            <div class="user-grid" id="userGrid">
    '''

    for i, participant in enumerate(participants, 1):
        html += f'''
                <div class="user-card" onclick="window.open('/', '_blank')">
                    <div class="user-rank">{i}</div>
                    <div class="user-avatar" style="background: {participant['avatar_color']};">{participant['avatar_text']}</div>
                    <div class="user-name">{participant['nickname']}</div>
                    <div class="user-rating" style="color: {participant['rank_color']};">{participant['rating']}</div>
                    <div class="user-tasks-score">Задач: {participant['tasks_score']}</div>
                    <div class="user-stats">
                        <div class="stat-item">
                            <div style="font-weight: bold;">Ранг</div>
                            <div style="color: {participant['rank_color']};">{participant['rank']}</div>
                        </div>
                        <div class="stat-item">
                            <div style="font-weight: bold;">Контестов</div>
                            <div>{participant['contests']}</div>
                        </div>
                        <div class="stat-item">
                            <div style="font-weight: bold;">Лучший рейтинг</div>
                            <div>{participant['best_rating']}</div>
                        </div>
                        <div class="stat-item">
                            <div style="font-weight: bold;">Последний контест</div>
                            <div>{participant['last_contest']}</div>
                        </div>
                    </div>
                </div>
        '''

    html += '''
            </div>

            <div class="contact-info">
                <p>Контакты для связи:</p>
                <p>
                    <i class="fab fa-telegram"></i> 
                    <a href="https://t.me/watlok" target="_blank">@watlok</a> • 
                    <i class="fas fa-envelope"></i> 
                    <a href="mailto:rewatlok@gmail.com">rewatlok@gmail.com</a>
                </p>
            </div>
        </div>

        <script>
            function filterUsers() {
                const searchInput = document.getElementById('searchInput');
                const searchTerm = searchInput.value.toLowerCase().trim();
                const userCards = document.querySelectorAll('.user-card');

                userCards.forEach(card => {
                    const userName = card.querySelector('.user-name').textContent.toLowerCase();
                    const matches = searchTerm === '' || userName.includes(searchTerm);
                    card.style.display = matches ? 'block' : 'none';
                });
            }
        </script>
    </body>
    </html>
    '''

    return html


if __name__ == '__main__':
    Path('contests').mkdir(exist_ok=True)
    Path('trainings').mkdir(exist_ok=True)
    Path('team_contests').mkdir(exist_ok=True)
    Path('math').mkdir(exist_ok=True)
    Path('news').mkdir(exist_ok=True)
    Path('contestants').mkdir(exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)
