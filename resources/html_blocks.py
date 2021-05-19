
HTML_STR = """<html>
<head>
  <style>
    table {
      text-align: left;
      position: relative;
      border-collapse: collapse;
    }
    td, th {
      padding: 8px;
      margin: 2px;
    }
    td {
      border-left: solid 1px black;
    }
    tr:nth-child(even) {background: #EEE}
    tr:nth-child(odd) {background: #FFF}
    tbody th:first-child {
      position: sticky;
      left: 0px;
      background: #fff;
    }
  </style>
</head>
<body>"""
