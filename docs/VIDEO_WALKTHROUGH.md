# Video Walkthrough

## 0:00-0:25 — Introduction

Hi, I’m Davit. I’ll walk you through a retail revenue and customer analytics project I built end to end. The goal was to take transaction-level data and turn it into a view that helps a retail team understand revenue performance, profitability, customer retention, and acquisition quality. This is a portfolio project using synthetic data, so it can be shared publicly without exposing confidential information.

## 0:25-0:55 — Pipeline

The workflow starts with raw transaction data. I used Python and pandas to clean and validate the data, calculate net revenue after discounts and returns, calculate gross profit, and create monthly business metrics. I then built RFM customer segmentation and cohort retention analysis. I also wrote SQL queries for monthly KPIs, category performance, customer value by acquisition channel, and top products. The final outputs feed this dashboard.

## 0:55-1:55 — Executive Overview

This first page is the executive overview. At the top I have the core KPIs: net revenue, gross profit, margin, orders, average order value, and return rate. With the full dataset, the project produces about 2.87 million dollars in net revenue, 1.22 million in gross profit, and a 42.4 percent profit margin across 10,083 orders. I included profit next to revenue because revenue growth alone can hide weak economics. The monthly chart shows how revenue and profit move over time, while the region and payment views help explain where the business is coming from. The filters on the left let a user drill into a specific region, product category, or acquisition channel without changing the underlying model.

## 1:55-2:50 — Customer Analytics

The second page focuses on customers. I used RFM analysis, which scores customers based on recency, frequency, and monetary value. That lets the business separate Champions and Loyal customers from At Risk or Hibernating customers and use different retention strategies for each group. Below that is a cohort retention heatmap. Instead of only looking at total customer counts, it tracks customers from their first purchase month and shows how many return in later months. That makes retention problems much easier to identify.

## 2:50-3:30 — Product and Channel Analytics

The final page looks at product and acquisition efficiency. In this dataset, Electronics generates the highest total category profit. I compare categories by both total profit and margin because the highest-revenue category is not always the most attractive category economically. I also compare acquisition channels using revenue per customer rather than only total revenue. Social comes out highest on revenue per customer in this generated dataset, which would make it a channel worth investigating for additional marketing investment.

## 3:30-3:55 — Decision Making and Close

The main value of the project is connecting analysis to decisions. A retail team could use these outputs to target retention campaigns, prioritize higher-value acquisition channels, understand which categories deserve inventory or promotional attention, and identify where returns or discounts are reducing profitability. Since this is synthetic data, I do not claim a measured real-world revenue impact. The project demonstrates how I would build and communicate the analysis needed to support those decisions.
