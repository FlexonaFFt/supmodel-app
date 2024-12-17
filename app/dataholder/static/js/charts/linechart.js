document.addEventListener("DOMContentLoaded", function () {
  const ctx = document.getElementById("lineChart").getContext("2d");
  const projectNumber = document
    .getElementById("myChart")
    .getAttribute("data-project-number");

  fetch(`/api/project-data/${projectNumber}/`)
    .then((response) => response.json())
    .then((data) => {
      const userInput = data.user_input;
      const predictions = data.lstm_time_predictions;

      const initialInvestments = Math.round(userInput.investments_m);
      const initialCrowdfunding = Math.round(userInput.crowdfunding_m);

      const adaptValue = (value, initialValue) => {
        const ratio = value / initialValue;
        if (ratio > 4) {
          return Math.round(value / 4);
        } else if (ratio > 3) {
          return Math.round(value / 2.5);
        } else if (ratio > 2) {
          return value;
        } else {
          return value;
        }
      };

      const predictedInvestments = predictions.map((pred) => {
        const investment = Math.round(pred.predicted_investments_m);
        const adaptedInvestment = adaptValue(investment, initialInvestments);
        return adaptedInvestment;
      });

      const predictedCrowdfunding = predictions.map((pred) => {
        const crowdfunding = Math.round(pred.predicted_crowdfunding_m);
        const adaptedCrowdfunding = adaptValue(
          crowdfunding,
          initialCrowdfunding,
        );
        return adaptedCrowdfunding;
      });

      // Вычисление общей суммы
      const totalSum = [
        initialInvestments + initialCrowdfunding,
        ...predictedInvestments.map(
          (inv, index) => inv + predictedCrowdfunding[index],
        ),
      ];

      const myChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: ["Start", "H1", "H2", "H3", "H4", "H5"],
          datasets: [
            {
              label: "Инвестиции",
              data: [initialInvestments, ...predictedInvestments],
              backgroundColor: "rgba(75, 192, 192, 0.2)",
              borderColor: "rgba(75, 192, 192, 1)",
              borderWidth: 2,
              tension: 0.4,
              fill: true,
            },
            {
              label: "Краудфандинг",
              data: [initialCrowdfunding, ...predictedCrowdfunding],
              backgroundColor: "rgba(255, 99, 132, 0.2)",
              borderColor: "rgba(255, 99, 132, 1)",
              borderWidth: 2,
              tension: 0.4,
              fill: true,
            },
            {
              label: "Общая сумма",
              data: totalSum,
              backgroundColor: "rgba(54, 162, 235, 0.2)",
              borderColor: "rgba(54, 162, 235, 1)",
              borderWidth: 2,
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: "Полугодия",
              },
            },
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: "Сумма $",
              },
              ticks: {
                stepSize: 2000,
              },
            },
          },
          plugins: {
            tooltip: {
              mode: "index",
              intersect: false,
            },
            legend: {
              position: "top",
              labels: {
                font: {
                  size: 14,
                },
              },
            },
          },
        },
      });
    });
});
