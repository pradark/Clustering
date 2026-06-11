# Customer Segmentation Analysis — ABC Debt Relief

Data-driven customer segmentation using K-Means clustering on 9,417 credit card customers, identifying five distinct behavioural segments to guide portfolio strategy and targeted outreach.

---

## Contents

| File | Description |
|------|-------------|
| [`Customer_Segmentation_Analysis.ipynb`](Customer_Segmentation_Analysis.ipynb) | Full analysis notebook with executed outputs |
| [`Customer_Segmentation_Deck.pdf`](Customer_Segmentation_Deck.pdf) | Executive presentation deck (11 slides) |

---

## Notebook Sections

1. **Setup & Imports** — libraries, colour palette, constants  
2. **Data Pull** — 9,417 customers, 18 features; data dictionary & summary stats  
3. **Missing Value Treatment** — tenure-stratified imputation, null visualisation  
4. **Exploratory Data Analysis** — distributions, box plots, correlation heatmap, scatter plots  
5. **Feature Engineering** — 7 derived metrics (Utilization Rate, Payment Quality, Engagement Score, Payment Consistency, Debt-to-Limit, Tenure Score, Transaction Volume)  
6. **Outlier Detection** — Isolation Forest (5% contamination), inlier vs outlier comparison  
7. **Preprocessing** — StandardScaler normalisation  
8. **Elbow Method** — Inertia curve k=1–15, marginal improvement, KneeLocator  
9. **Silhouette & Validation Metrics** — Silhouette, Davies-Bouldin, Calinski-Harabasz for k=2–13  
10. **Model Comparison** — K-Means vs Hierarchical vs DBSCAN vs GMM  
11. **Final Model (k=5)** — Centroid heatmap, segment sizing, naming  
12. **PCA Visualisation** — Scree plot, 2D cluster scatter  
13. **Segment Profiles & Spider Charts** — Radar charts + deep-dive per segment  
14. **Portfolio & ROI** — Summary table, investment vs benefit analysis  
15. **Recommendations** — 90-day roadmap, executive dashboard  

---

## The Five Segments

| Segment | Profile |
|---------|---------|
| **Distressed Revolvers** | High balance, low payments — highest intervention priority |
| **Prime Customers** | Low utilisation, consistent payers — retention focus |
| **Engaged Optimisers** | Active purchasers, solid payment behaviour — upsell opportunity |
| **Low Capacity** | Low spend, limited credit — financial wellness programmes |
| **High Risk / New** | Short tenure, high utilisation — early engagement critical |

---

## Tech Stack

`pandas` · `scikit-learn` · `matplotlib` · `seaborn` · `scipy` · `kneed` · `plotly`

---

*Prepared for ABC Debt Relief — June 2026 · Confidential*
