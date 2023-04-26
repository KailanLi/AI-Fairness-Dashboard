function updateVisualization(selectedFairnessDefinition) {
    // Clear the current visualization
    d3.select("#visualization").html("");

    // Update the visualization based on the selected fairness definition
    switch (selectedFairnessDefinition) {
        case "statisticalParity":
            // Code to generate visualization for statistical parity
            break;
        case "equalOpportunity":
            // Code to generate visualization for equal opportunity
            break;
        case "equalizedOdds":
            // Code to generate visualization for equalized odds
            break;
    }
}



function populateAttributeDropdowns(attributes) {
    let sensitiveAttributesSelect = document.getElementById("sensitiveAttributes");
    let targetAttributeSelect = document.getElementById("targetAttribute");

    // Clear the current options
    sensitiveAttributesSelect.innerHTML = "";
    targetAttributeSelect.innerHTML = "";

    attributes.forEach((attribute) => {
        // Create options for sensitive attributes
        let sensitiveOption = document.createElement("option");
        sensitiveOption.value = attribute;
        sensitiveOption.text = attribute;
        sensitiveAttributesSelect.add(sensitiveOption);

        // Create options for target attribute
        let targetOption = document.createElement("option");
        targetOption.value = attribute;
        targetOption.text = attribute;
        targetAttributeSelect.add(targetOption);
    });
}



function displayAttributeSelection(parsedData) {
    // Get column names
    let columns = Object.keys(parsedData[0]);

    // Generate form for selecting sensitive and target attributes
    let formHtml = `
        <label for="sensitiveAttribute">Sensitive Attributes:</label>
        <select id="sensitiveAttributes">
            ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
        </select>
        <br>
        <label for="targetAttribute">Target Attribute:</label>
        <select id="targetAttribute">
            ${columns.map(col => `<option value="${col}">${col}</option>`).join('')}
        </select>
        <br>
        <button id="generateVisual">Generate Visualization</button>
    `;

    document.getElementById('attributeSelection').innerHTML = formHtml;
    document.getElementById('attributeSelection').style.display = 'block'; // Show the attribute selection div
    document.getElementById("fairnessDefinitions").style.display = "block";


    
    // Add event listener for the generate visualization button
    document.getElementById("generateVisual").addEventListener("click", function () {
        let sensitiveAttribute = document.getElementById("sensitiveAttributes").value;
        let targetAttribute = document.getElementById("targetAttribute").value;    
        // Clear the current data table
        d3.select("#dataTableContainer").html("");
    
        // Generate a new data table with the selected sensitive and target attributes
        createDataTable(parsedData, sensitiveAttribute, targetAttribute);
    
        // Generate the grouped bar chart
        generateGroupedBarChart(parsedData, sensitiveAttribute, targetAttribute);

        console.log('Generate visualization button clicked');
    });

    // Call the createDataTable function to populate the table
    createDataTable(parsedData);
}


document.addEventListener("DOMContentLoaded", () => {


    const inputFile = document.getElementById("inputFile");
    if (inputFile) {
        inputFile.addEventListener("change", function (event) {
            let file = event.target.files[0];
            let reader = new FileReader();

            reader.onload = function (e) {
                let data = e.target.result;
                let parsedData;

                if (file.name.endsWith(".csv")) {
                    parsedData = d3.csvParse(data);
                } else if (file.name.endsWith(".json")) {
                    parsedData = JSON.parse(data);
                } else {
                    alert("Unsupported file format. Please upload a CSV or JSON file.");
                    return;
                }

                // Get column names
                let columns = Object.keys(parsedData[0]);

                // Call the populateAttributeDropdowns function
                populateAttributeDropdowns(columns);

                displayAttributeSelection(parsedData);
            };

            reader.readAsText(file);
        });
    }
});


function generateGroupedBarChart(data, sensitiveAttribute, targetAttribute) {
    // Prepare the data for visualization
    let groupedData = d3.nest()
        .key(d => d[sensitiveAttribute])
        .key(d => d[targetAttribute])
        .rollup(v => v.length)
        .entries(data);
    console.log("Grouped data:", groupedData);

    // Define chart dimensions and margins
    const margin = {top: 20, right: 20, bottom: 40, left: 40};
    const width = 500 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    // Create a tooltip element
    const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);


    // Define x and y scales
    const x0 = d3.scaleBand()
        .domain(groupedData.map(d => d.key))
        .rangeRound([0, width])
        .paddingInner(0.1);

    const x1 = d3.scaleBand()
        .domain(groupedData[0].values.map(d => d.key))
        .rangeRound([0, x0.bandwidth()])
        .padding(0.05);

    const y = d3.scaleLinear()
        .domain([0, d3.max(groupedData, d => d3.max(d.values, d1 => d1.value))])
        .rangeRound([height, 0]);

    // Define x and y axis
    const xAxis = d3.axisBottom(x0);
    const yAxis = d3.axisLeft(y);

    // Create the SVG element
    const svg = d3.select(".visualization-container").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Append the x axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Append the y axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    // Create the bars
    const sensitiveAttr = svg.selectAll(".sensitiveAttr")
        .data(groupedData)
        .enter().append("g")
        .attr("class", "sensitiveAttr")
        .attr("transform", d => "translate(" + x0(d.key) + ",0)");

        sensitiveAttr.selectAll("rect")
        .data(d => d.values)
        .enter().append("rect")
        .attr("width", x1.bandwidth())
        .attr("x", d => x1(d.key))
        .attr("y", d => y(d.value))
        .attr("height", d => height - y(d.value))
        .attr("fill", (d, i) => d3.schemeCategory10[i])
        .on("mouseover", function (d, i, nodes) {
    const parentData = d3.select(nodes[i].parentNode).datum();

    // Show tooltip
    tooltip.transition()
        .duration(200)
        .style("opacity", .9);
    tooltip.html("Value: " + d.value)
        .style("left", (d3.event.pageX + 5) + "px")
        .style("top", (d3.event.pageY - 28) + "px");
    
            // Highlight the corresponding row in the table
            d3.select("#fairnessMetricResults")
                .selectAll("tr")
                .classed("highlighted", row => row.key === d.key);
        })
        .on("mouseout", function () {
            // Hide tooltip
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
    
            // Remove the highlight from the table rows
            d3.select("#fairnessMetricResults")
                .selectAll("tr")
                .classed("highlighted", false);
        })
        .on("click", function (d, i, nodes) {
            const parentData = d3.select(nodes[i].parentNode).datum();
        
            // Filter the data based on the selected bar
            const filteredData = data.filter(row => row[sensitiveAttribute] === parentData.key && row[targetAttribute] === d.key);
        
            // Update the table
            updateDataTable(filteredData.slice(0, 5), sensitiveAttribute, targetAttribute);
        });
    

    sensitiveAttr.selectAll("rect")
        .data(d => d.values)
        .enter().append("rect")
        .attr("width", x1.bandwidth())
        .attr("x", d => x1(d.key))
        .attr("y", d => y(d.value))
        .attr("height", d => height - y(d.value))
        .attr("fill", (d, i) => d3.schemeCategory10[i]);

        const legend = svg.selectAll(".legend")
        .data(groupedData[0].values.map(d => d.key))
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", (d, i) => "translate(0," + i * 20 + ")");
    
        legend.append("rect")
            .attr("x", width - 18)
            .attr("width", 18)
            .attr("height", 18)
            .attr("fill", (d, i) => d3.schemeCategory10[i]);
        
        legend.append("text")
            .attr("x", width - 24)
            .attr("y", 9)
            .attr("dy", ".35em")
            .style("text-anchor", "end")
            .text(d => d);
}

function createDataTable(data, sensitiveAttribute, targetAttribute) {
    // Get column names
    const columns = Object.keys(data[0]);

    // Get top 5 rows
    const topRows = data.slice(0, 5);

    const combinedRows = topRows
    // Create table
    const table = d3.select("#dataTableContainer")
        .classed("table-container", true)
        .append("table")
        .attr("class", "table");

    // Create table header
    const thead = table.append("thead");
    thead.append("tr")
        .selectAll("th")
        .data(columns)
        .enter()
        .append("th")
        .classed("sensitive-column", d => d === sensitiveAttribute)
        .classed("target-column", d => d === targetAttribute)
        .text(d => d);

    // Create table body
    const tbody = table.append("tbody");
    tbody.selectAll("tr")
        .data(combinedRows)
        .enter()
        .append("tr")
        .selectAll("td")
        .data(row => columns.map(column => ({ value: row[column], column })))
        .enter()
        .append("td")
        .classed("sensitive-column", d => d.column === sensitiveAttribute)
        .classed("target-column", d => d.column === targetAttribute)
        .text(d => d.value);
}

function updateDataTable(newData, sensitiveAttribute, targetAttribute) {
    const columns = Object.keys(newData[0]);

    // Remove the existing table body
    d3.select("#dataTableContainer").select("tbody").remove();

    // Create a new table body with the newData
    const tbody = d3.select("#dataTableContainer").select("table").append("tbody");
    tbody.selectAll("tr")
        .data(newData)
        .enter()
        .append("tr")
        .selectAll("td")
        .data(row => columns.map(column => ({ value: row[column], column })))
        .enter()
        .append("td")
        .classed("sensitive-column", d => d.column === sensitiveAttribute)
        .classed("target-column", d => d.column === targetAttribute)
        .text(d => d.value);
}