function get_children(node, type)
{
	if (type)
		type = type.toLowerCase();
	var result = [];
	for (var i = 0; i < node.childNodes.length; ++i)
	{
		var child = node.childNodes[i];
		if (child.nodeType == 1 && (!type || (child.nodeName.toLowerCase() == type)))
			result.push(child);
	}
	return result;
}

function get_nth_child(node, count, type)
{
	if (!count)
		count = 0;
	if (type)
		type = type.toLowerCase();
	for (var i = 0; i < node.childNodes.length; ++i)
	{
		var child = node.childNodes[i];
		if (child.nodeType == 1 && (!type || (child.nodeName.toLowerCase() == type)))
			if (!count--)
				return child;
	}
	return null;
}

function get_first_text(node)
{
	while (node.nodeType != 3)
	{
		if (!node.childNodes.length)
			return null;
		node = node.childNodes[0];
	}
	return node.nodeValue;
}

function get_filename(tr)
{
	return get_first_text(get_nth_child(tr, 0, "th"));
}

function get_nroflines(tr)
{
	return parseInt(get_first_text(get_nth_child(tr, 0, "td")), 10);
}

function get_coverablelines(tr)
{
	return parseInt(get_first_text(get_nth_child(tr, 1, "td")), 10);
}

function get_coveredlines(tr)
{
	return parseInt(get_first_text(get_nth_child(tr, 2, "td")), 10);
}

function get_coverage(tr)
{
	var content = get_first_text(get_nth_child(tr, 3, "td"));
	if (content == "n/a")
		return -1.0;
	return parseFloat(content);
}

var files_rows = null;

function files_prepare()
{
	var tbody = document.getElementById("files");
	rows = get_children(tbody, "tr");
	for (var i = 0; i < rows.length; ++i)
	{
		var row = rows[i];
		row.filename = get_filename(row);
		row.nroflines = get_nroflines(row);
		row.coverablelines = get_coverablelines(row);
		row.coveredlines = get_coveredlines(row);
		row.coverage = get_coverage(row);
	}

	var button;
	
	button = document.createElement("span");
	button.innerHTML = "A-Z";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbyfilename_asc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbyfilename_asc);");
	document.getElementById("filename").appendChild(button);

	button = document.createElement("span");
	button.innerHTML = "Z-A";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbyfilename_desc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbyfilename_desc);");
	document.getElementById("filename").appendChild(button);
	
	button = document.createElement("span");
	button.innerHTML = "1-9";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbynroflines_asc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbynroflines_asc);");
	document.getElementById("nroflines").appendChild(button);

	button = document.createElement("span");
	button.innerHTML = "9-1";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbynroflines_desc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbynroflines_desc);");
	document.getElementById("nroflines").appendChild(button);
	
	button = document.createElement("span");
	button.innerHTML = "1-9";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbycoverablelines_asc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbycoverablelines_asc);");
	document.getElementById("coverablelines").appendChild(button);

	button = document.createElement("span");
	button.innerHTML = "9-1";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbycoverablelines_desc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbycoverablelines_desc);");
	document.getElementById("coverablelines").appendChild(button);
	
	button = document.createElement("span");
	button.innerHTML = "1-9";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbycoveredlines_asc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbycoveredlines_asc);");
	document.getElementById("coveredlines").appendChild(button);

	button = document.createElement("span");
	button.innerHTML = "9-1";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbycoveredlines_desc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbycoveredlines_desc);");
	document.getElementById("coveredlines").appendChild(button);

	button = document.createElement("span");
	button.innerHTML = "1-9";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbycoverage_asc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbycoverage_asc);");
	document.getElementById("coverage").appendChild(button);

	button = document.createElement("span");
	button.innerHTML = "9-1";
	if (document.all)
		button.onclick = function(){return files_sort(files_cmpbycoverage_desc);}
	else
		button.setAttribute("onclick", "return files_sort(files_cmpbycoverage_desc);");
	document.getElementById("coverage").appendChild(button);
}

function files_sort(sorter)
{
	document.body.setAttribute("class", "wait");

	function dosort()
	{
		rows.sort(sorter);
	
		var tbody = document.getElementById("files");
		for (var i = 0; i < rows.length; ++i)
			tbody.appendChild(rows[i]);
	
		document.body.setAttribute("class", "nowait");
	}
	window.setTimeout(dosort, 0.01);
	return false;
}

function files_cmpbyfilename_asc(tr1, tr2)
{
	var fn1 = tr1.filename;
	var fn2 = tr2.filename;
	if (fn1>fn2)
		return 1;
	else if (fn1<fn2)
		return -1;
	return 0;
}

function files_cmpbyfilename_desc(tr1, tr2)
{
	var fn1 = tr1.filename;
	var fn2 = tr2.filename;
	if (fn1<fn2)
		return 1;
	else if (fn1>fn2)
		return -1;
	return 0;
}

function files_cmpbynroflines_asc(tr1, tr2)
{
	return tr1.nroflines-tr2.nroflines;
}

function files_cmpbynroflines_desc(tr1, tr2)
{
	return tr2.nroflines-tr1.nroflines;
}

function files_cmpbycoverablelines_asc(tr1, tr2)
{
	return tr1.coverablelines-tr2.coverablelines;
}

function files_cmpbycoverablelines_desc(tr1, tr2)
{
	return tr2.coverablelines-tr1.coverablelines;
}

function files_cmpbycoveredlines_asc(tr1, tr2)
{
	return tr1.coveredlines-tr2.coveredlines;
}

function files_cmpbycoveredlines_desc(tr1, tr2)
{
	return tr2.coveredlines-tr1.coveredlines;
}

function files_cmpbycoverage_asc(tr1, tr2)
{
	return tr1.coverage-tr2.coverage;
}

function files_cmpbycoverage_desc(tr1, tr2)
{
	return tr2.coverage-tr1.coverage;
}
