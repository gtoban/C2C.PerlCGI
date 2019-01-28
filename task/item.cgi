#!/usr/bin/perl
use cPanelUserConfig;
use strict;
use warnings;

use Date::Calc qw(Days_in_Month Today_and_Now);
use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use clientManager qw(:Client :Clientcheck);
use Manager qw(:User :Usercheck);
use htmlManager qw(:elements);
use itemDatabase qw(:Tags :Itemtag :Itemuser :Item :Itemgroups :Note :ItemToItem);
use general qw(:addUpdate :get :check);

my $cgi = CGI->new;
my $sid = $cgi->cookie('CGISESSID') || $cgi->param('CGISESSID') || undef;
my $session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});

my $userrights = 0;
my $userid = "";
my $userfirstname = "";
my $userlastname = "";
my $useremail = "";
my $userclientid = "";
if ($session->param("userid"))
{
	$userid = $session->param("userid");
	$userfirstname = $session->param("userfirstname");
	$userlastname = $session->param("userlastname");
	$useremail = $session->param("useremail");
	$userclientid = $session->param("userclientid");
	$userrights = $session->param("userrights");
}else
{
	print $cgi->redirect(-url=>'http://www.c2c-hit.net/c2cmobile/login.cgi');			
}

#initial values
#populate values
my $itemid;
my $hold;
my $item;
my $showlog = 0;

my $message = "";


my $itemwasadded = 0;

my $newtagname;

#test form values and untaint

if ($cgi->param('mytags') )
{
	my @tags = $cgi->param('tags');
	$itemid = $cgi->param('itemid');
	my $nomatch = 1;
	my @addtags;
	my $addresult;
	my %keeptags;
	my @removetags;
	my $removeresult;
	$hold = getAnySort(["SELECT * FROM itemtotag i WHERE i.itemid = $itemid AND NOT EXISTS (SELECT * FROM itemtag t WHERE i.tagid = t.id AND t.tagdefault = 1)",0,0,0]);
	my $count = 0;
	foreach my $tag (@tags)
	{
		$nomatch = 1;
		foreach my $etag (@{$hold->[0]})
		{
			if ($etag->{'tagid'} == $tag)
			{
				$nomatch = 0;
				$keeptags{$etag->{'tagid'}} = 1;
			}
			
		}
		if ($nomatch)
		{
			$addtags[$count] = $tag;
			$count += 1;
		}
	}
	

	if (@addtags)
	{
		$addresult = addItemTags([$itemid, \@addtags, $userid]);
		if ($addresult->[0])
		{
			$message .= "Tags Added. "
		}else
		{
			$message .= "Tag Add Error: $addresult->[1] :$addresult->[2]";
		}
	}

	$count = 0;
	foreach my $etag (@{$hold->[0]})
	{
		if (!$keeptags{$etag->{'tagid'}})
		{
			$removetags[$count] = $etag->{'tagid'};
			$count += 1;
		}
	}

	if (@removetags)
	{
		$removeresult = deleteItemTags([$itemid, \@removetags, $userid]);
		if ($removeresult->[0])
		{
			$message .= " Tags Removed. "
		}else
		{
			$message .= " Tag Remove Error: $removeresult->[1] :$removeresult->[2]";
		}
	}
	
	#remove @removetags
	
}elsif ($cgi->param('addtag'))
{
	my $addtag = $cgi->param('addtag');
	if (checkName($addtag))
	{
		my $addtagresult = addUpdateSimple("INSERT INTO itemtag (name, tagdefault, active) VALUES ('$addtag', 0, 1)");
		if ($addtagresult->[0])
		{
			$message .= "Tag Added";
		}else
		{
			$message .= "Error: $addtagresult->[1] : $addtagresult->[2]";
		}
	}else
	{
		$message .= "Bad Tag";
	}
	
	
}elsif ($cgi->param('myusers'))
{
	my @users = $cgi->param('users');
	$itemid = $cgi->param('itemid');
	my $nomatch = 1;
	my @addusers;
	my $addresult;
	my %keepusers;
	my @removeusers;
	my $removeresult;
	$hold = getAnySort(["SELECT * FROM itemtouser WHERE itemid = $itemid",0,0,0]);
	my $count = 0;
	foreach my $user (@users)
	{
		$nomatch = 1;
		foreach my $euser (@{$hold->[0]})
		{
			if ($euser->{'userid'} == $user)
			{
				$nomatch = 0;
				$keepusers{$euser->{'userid'}} = 1;
			}
			
		}
		if ($nomatch)
		{
			$addusers[$count] = $user;
			$count += 1;
		}
	}
	

	if (@addusers)
	{
		$addresult = addItemUser([$itemid, \@addusers, $userid]);
		if ($addresult->[0])
		{
			$message .= "Users Added. "
		}else
		{
			$message .= "User Add Error: $addresult->[1] :$addresult->[2]";
		}
	}

	$count = 0;
	foreach my $euser (@{$hold->[0]})
	{
		if (!$keepusers{$euser->{'userid'}})
		{
			$removeusers[$count] = $euser->{'userid'};
			$count += 1;
		}
	}

	if (@removeusers)
	{
		$removeresult = deleteItemUser([$itemid, \@removeusers, $userid]);
		if ($removeresult->[0])
		{
			$message .= " Users Removed. "
		}else
		{
			$message .= " User Remove Error: $removeresult->[1] :$removeresult->[2]";
		}
	}
	
	#remove @removetags
}elsif ($cgi->param('myinfo'))
{
	$itemid = $cgi->param('itemid');
	my $newclient = $cgi->param('client');
	my $newname = $cgi->param('name');
	my $newdescription = $cgi->param('description');
	my $newstatus = $cgi->param('status');
	
	my $newstartyear = $cgi->param('yearstart');
	my $newstartmonth = $cgi->param('monthstart');
	my $newstartday = $cgi->param('daystart');
	my $newstarthour = $cgi->param('hourstart');
	my $newstartmin = $cgi->param('minstart');
	
	my $newendyear = $cgi->param('yearend');
	my $newendmonth = $cgi->param('monthend');
	my $newendday = $cgi->param('dayend');
	my $newendhour = $cgi->param('hourend');
	my $newendmin = $cgi->param('minend');

	my $newstartdate = "$newstartyear-$newstartmonth-$newstartday $newstarthour:$newstartmin:00";
	my $newenddate = "$newendyear-$newendmonth-$newendday $newendhour:$newendmin:00";
	
	
	my $update;
	my $go = 1;
	

	$hold = getAnySort(["SELECT * FROM item WHERE id = $itemid", 0, 0, 0]);
	if ($newclient != $hold->[0][0]{'clientid'})
	{
		$update->{'clientid'} = $newclient;
	}
	if ($newname ne $hold->[0][0]{'name'})
	{
		if (checkTheseWords($newname))
		{
			$update->{'name'} = $newname;
		}else
		{
			$go = 0;
			$message .= "Bad Description";
		}
	}
	if ($newdescription ne $hold->[0][0]{'description'})
	{
		if (checkTheseWords($newdescription))
		{
			$update->{'description'} = $newdescription;
		}else
		{
			$go = 0;
			$message .= " Bad Description";
		}
	}
	if ($newstatus != $hold->[0][0]{'statusid'})
	{
		$update->{'statusid'} = $newstatus;
	}
	if ($newstartdate ne $hold->[0][0]{'startdate'})
	{
	    if ($newstartdate)
	    {
		$update->{'startdate'} = $newstartdate;
	    }else
	    {
		$update->{'startdate'} = "NULL";
	    }
	}
	if ($newenddate ne $hold->[0][0]{'enddate'})
	{
	    if ($newenddate)
	    {
		$update->{'enddate'} = $newenddate;
	    }else
	    {
		$update->{'enddate'} = "NULL";
	    }
	}
	
	if ($update && $go)
	{
		my $updateinfo = [$userid, $itemid, $update];
		$hold = addEditItem($updateinfo);
		if ($hold->[0])
		{
			$message .= " Gen Info Updated. "
		}else
		{
			$message .= " Gen Info Update Error: $hold->[1] :$hold->[2]";
		}
		
	}
}elsif ($cgi->param('mylog'))
{
	$itemid = $cgi->param('itemid');
	my $note = $cgi->param('note');
	
	if (1)#checkTheseWords($note))
	{
		logLastEdit($itemid, $note, $userid, 0);
		$message .= "Note was good";
	}else
	{
		$message .= "Bad Note $note";
	}
}elsif ($cgi->param('showlog'))
{
	$showlog = 1;
}elsif ($cgi->param('myownedgroups'))
{
	$itemid = $cgi->param('itemid');
	my $name = $cgi->param('name');
	my $description = $cgi->param('description');

	if (!$name)
	{
		$message .= "Name must be provided.";
	}elsif (!$description)
	{
		$message .= "Description must be provided.";
	}elsif (!checkTheseWords($name))
	{
		$message .= "Bad Name";
	}elsif (!checkTheseWords($description))
	{
		$message .= "Bad description.";
	}else
	{
		$hold = addItemGroups([0,$userid, {name => $name, description =>$description, itemid => $itemid}]);
		if ($hold->[0])
		{
			$message .= "Group Added.";
		}else
		{
			$message .= "Group NOT Added. $hold->[1] : $hold->[2]";
		}
	}
}elsif ($cgi->param('myremovegroups'))
{
	$itemid = $cgi->param('itemid');
	$hold = deleteItemGroups($cgi->param('groupid'));
	if ($hold->[0])
	{
		$message .= "Group Removed";
	}else
	{
		$message .= "Group NOT Removed. $hold->[1] : $hold->[2]";
	}
}elsif ($cgi->param('removeitem'))
{
    $itemid = $cgi->param('itemid');
    my $removeitemid = $cgi->param('removeitemid');
    $hold = deleteItemToItem($itemid, $removeitemid, $userid);
    if ($hold->[0])
    {
	$message .= "Item Removed";
    }else
    {
	$message .= "Item NOT Removed. $hold->[1] : $hold->[2]";
    }
}

$itemid = $cgi->param('itemid');

$hold = getAny(['item', 0, ['n', 'id', $itemid]]);
if ($hold->[1])
{
	$item = $hold->[0][0];
}else
{
	$message .= "NOPE: $hold->[2]: $hold->[3]\n";
}

#HTML with FORM

print $cgi->header();
my $javascript = "<script>\n";
$javascript .= "function confirmDelete() {\n";
$javascript .= "return confirm('Are you sure you want to delete this?');\n";
$javascript .= "}\n";
$javascript .= "</script>\n";
print jqheader($javascript);

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Task", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

#print "<p>$message</p>";
print "<h1>". getMyTagDefault($itemid) . "</h1>\n";
if ($userrights > 1)
{    
    print "<div class=\"ui-grid-a\">\n";
    print "<div class=\"ui-block-a\">\n";
    print "<form method=\"post\">\n";
    print getMyTags($itemid);
    print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
    print "<input type=\"submit\" name=\"mytags\" value=\"Update\">\n";
    print "</form>\n";
    print "<form method=\"post\">\n";
    print textInput({'name' => 'addtag', 'label' => 'Add Tag'});
    print "<button type=\"submit\" name=\"newtag\" class=\"ui-btn ui-shadow ui-corner-all ui-btn-icon-notext ui-icon-plus\"></button>";
    print "</form>\n";
    print "</div>";
    print "<div class=\"ui-block-b\">\n";
    print "<form method=\"post\">\n";
    print getMyUsers($itemid);
    print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
    print "<input type=\"submit\" name=\"myusers\" value=\"Update\">\n";
    print "</form>\n";
    print "</div>\n";
    print "</div>\n";
}

print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print "<h2>General Info</h2>\n";
print "<form method=\"post\">\n";
print getMyClients($item->{'clientid'}) . "\n";
print textInput({
		'name' => "name",
		'label' => "Name",
		'value' => $item->{'name'}}) ."\n";
print textArea({
		'name' => "description",
		'label' => "Description",
		'value' => $item->{'description'}}) ."\n";
print getMyStatus($item->{'statusid'}) . "\n";
print getMyCreator($item->{'userid'}) . "\n";
if ($userrights > 1)
{
    print getMyDates($item);
}
print "<label for=\"createdate\">Create Date</label>\n";
print "<input type=\"text\" id=\"createdate\" readonly value=\"$item->{'createdate'}\">\n";
print "<label for=\"lasteditdate\">Last Edit Date</label>\n";
print "<input type=\"text\" id=\"lasteditdate\" readonly value=\"$item->{'lasteditdate'}\">\n";
print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
print "<input type=\"submit\" name=\"myinfo\" value=\"Update\">\n";
print "</form>\n";
print "</div>";
print "<div class=\"ui-block-b\">\n";
print "<h2>Log</h2>\n";
print "<label for=\"note\">Log Notes</label>\n";
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\" style=\"height:800px;width:100\%\">\n";
print "<textarea name=\"note\" id=\"note\" readonly>\n";
print getMyLog($itemid, $showlog);
print "</textarea>\n";
print "</div>\n";
print "<div class=\"ui-block-b\" style=\"height:800px;width:0\%\">\n";
print "</div>\n";
print "</div>\n";
if ($userrights > 1)
{
    print "<form method=\"post\">\n";
    print textArea({'name' => 'note', 'label' => 'note', 'value' => ''});
    print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
    print "<input type=\"submit\" name=\"mylog\" value=\"Add New Note\">\n";
    print "</form>\n";
    if ($userrights > 2)
    {
	print "<form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/task/editlog.cgi\" >\n";
	print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
	print "<input type=\"submit\" name=\"submit\" value=\"Edit Log\">\n";
	print "</form>\n";
    }
}
print "<form method=\"post\" >\n";
print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
print "<input type=\"submit\" name=\"showlog\" value=\"Show Log\">\n";
print "</form>\n";
print "</div>\n";
print "</div>\n";

if ($userrights > 1)
{
    print "<div class=\"ui-grid-a\">\n";
    print "<div class=\"ui-block-a\">\n";
    print "<h2>Owned Groups</h2>\n";
    print getMyOwnedGroups($itemid);
    print "<form method=\"post\">\n";
    print textInput({'name' => 'name', 'label' => 'Name', 'value' => ''});
    print textArea({'name' => 'description', 'label' => 'Description', 'value' => ''});
    print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
    print "<input type=\"submit\" name=\"myownedgroups\" value=\"Add New\">\n";
    print "</form>\n";
    print "</div>";
    print "<div class=\"ui-block-b\">\n";
    print "<h2>Groups</h2>\n";
    print getMyGroups($itemid);
    print "<form method=\"post\">\n";
    print "</form>\n";
    print "</div>\n";
    print "</div>\n";

    print "<h2>Associated Items</h1>\n";
    print getMyItems($itemid);
    print "<form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/task/itemsearch.cgi\" target=\"_blank\">\n";
    print "<input type=\"hidden\" name=\"itemid\" value=\"$item->{'id'}\">\n";
    print "<input type=\"submit\" name=\"myassociateditems\" value=\"Add New\">\n";
    print "</form>\n";
}


print "</div>\n";


if ($message)
{
    print "<script> alert(\"$message\")</script>";
}


print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();

sub getMyTagDefault
{
	my $itemid = shift;
	my $tags;
	my $hold = getAnySort(["SELECT t.name FROM itemtag t WHERE t.tagdefault = 1 AND EXISTS (SELECT * FROM itemtotag i WHERE t.id = i.tagid AND itemid = $itemid)", 0,
	                     0,
			     0]);
	if ($hold->[1])
	{
		$tags = $hold->[0][0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}

	return $tags->{'name'};
}

sub getMyTags
{
	my $item = shift;
	my $mytags;
	my @selected;
	my $hold = getAnySort(["SELECT * FROM itemtotag WHERE itemid = $item", 0,
                   0,
		   0]);
	if ($hold->[1])
	{
		$mytags = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}
	my $count = 0;
	foreach my $tag (@{$mytags})
	{
		$selected[$count] = $tag->{'tagid'};
		$count += 1;
	}
	my $options;
	
	my $taginfo = getTags({ 'default' => 0});
	my $tags = $taginfo->[0];
	foreach my $tag (@{$tags})
	{
		if ($tag->{'id'} != 1 && $tag->{'tagdefault'} == 0)
		{
			$options->{$tag->{'id'}} = $tag->{'name'};
		}
	}
	my $info = {
	      'blankoption' => 0,
	      'multiple' => 1,
	      'options' => $options,
	      'selected' => \@selected,
	      'name' => 'tags',
	      'label' => 'Tags'
	};

	if ($options)
	{
		return selectList($info);
	}else
	{
		return "<p>No Tag</p>";
	}

	
}

sub getMyUsers
{
	my $item = shift;
	my $myusers;
	my $users;
	my @selected;
	my %options;
	my $hold = getAnySort(["SELECT * FROM itemtouser WHERE itemid = $item", 0,
                   0,
		   0]);
	if ($hold->[1])
	{
		$myusers = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}
	my $count = 0;
	foreach my $user (@{$myusers})
	{
		$selected[$count] = $user->{'userid'};
		$count += 1;
	}

	$hold = getAnySort(["SELECT * FROM users WHERE rights != 1", 0,
                   0,
		   0]);
	if ($hold->[1])
	{
		$users = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}
	$count = 0;
	foreach my $user (@{$users})
	{
		$options{$user->{'id'}} = "$user->{'firstName'} $user->{'lastName'}";
		$count += 1;
	}
	
	my $info = {
	      'blankoption' => 0,
	      'multiple' => 1,
	      'options' => \%options,
	      'selected' => \@selected,
	      'name' => 'users',
	      'label' => 'Associated People'
	};

	return selectList($info);
	
}

sub getMyClients
{
	my $cid = shift;
	my @clients = getClients();
	my %clienthash;
	foreach my $client (@clients)
	{
		$clienthash{"$client->{'clientid'}"} = $client->{'name'};
	}
	my $info = {
	      'blankoption' => 0,
	      'multiple' => 0,
	      'options' => \%clienthash,
	      'selected' => [$cid],
	      'name' => 'client',
	      'label' => 'Client'
	};

	return selectList($info);
	      
	
}

sub getMyStatus
{
	my $sid = shift;
	my %options;
	my $statuses;
	my $hold = getAnySort(['SELECT * FROM itemstatus', 0,
                   0,
		   0]);
	if ($hold->[1])
	{
		$statuses = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}
	foreach my $status (@{$statuses})
	{
		$options{$status->{'id'}} = $status->{'name'};
	}
	my $info = {
	      'blankoption' => 1,
	      'multiple' => 0,
	      'options' => \%options,
	      'selected' => [$sid],
	      'name' => 'status',
	      'label' => 'Status'
	};

	return selectList($info);
}

sub getMyCreator
{
	my $userid = shift;
	my $user;
	my $value = "";
	#return "SELECT * FROM users WHERE id = $userid";
	my $hold = getAnySort(["SELECT * FROM users WHERE id = $userid", 0,
                   0,
		   0]);
	if ($hold->[1])
	{
		$user = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}
	$value .= "<label for=\"creator\">Creator</label>\n";
        $value .= "<input type=\"text\" id=\"creator\" readonly value=\"$user->[0]{'firstName'} $user->[0]{'lastName'}\">\n";
	return $value;
}

sub getMyDates
{
    my $titem = shift;
    my $tstart = $titem->{'startdate'};
    my $tend = $titem->{'enddate'};
    my $dates = "";
    my @firstsplit;
    my @datesplit;
    my @timesplit;
    $dates .= "<p>Start Time </p>";    
    if ($tstart)
    {
	@firstsplit = split / /, $tstart;
	@datesplit = split /-/, $firstsplit[0];
	@timesplit = split /:/, $firstsplit[1];
	
	$dates .= datetimepicker("start", $datesplit[0], $datesplit[1], $datesplit[2], $timesplit[0], $timesplit[1]);
    }else
    {
	$dates .= datetimepicker("start");
    }

    $dates .= "<p>End Time </p>";
    if ($tend)
    {
	@firstsplit = split / /, $tend;
	@datesplit = split /-/, $firstsplit[0];
	@timesplit = split /:/, $firstsplit[1];
	
	$dates .= datetimepicker("start", $datesplit[0], $datesplit[1], $datesplit[2], $timesplit[0], $timesplit[1]);
    }else
    {
	$dates .= datetimepicker("end");
    }
}

sub getMyLog
{
	my $item = shift;
	my $log = shift;
	my $notes;
	my $input = "";
	my $hold;
	if ($log)
	{
		$hold = getAnySort(["SELECT n.note, n.createdate, CONCAT( u.firstName,  ' ', u.lastName ) as 'name' FROM itemnote n JOIN users u on n.userid = u.id WHERE n.itemid = $itemid ORDER BY createdate DESC", 0,
                   0,
		   0]);
	}else
	{
		$hold = getAnySort(["SELECT n.note, n.createdate, CONCAT( u.firstName,  ' ', u.lastName ) as 'name' FROM itemnote n JOIN users u on n.userid = u.id WHERE n.itemid = $itemid AND n.log = 0 ORDER BY createdate DESC", 0,
                   0,
		   0]);
	}
	if ($hold->[1])
	{
		$notes = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}
	foreach my $note (@{$notes})
	{
		$input .= "-- $note->{'name'} --&#13;&#10;";
		$input .= "-- $note->{'createdate'} --&#13;&#10;";
		$input .= "$note->{'note'}&#13;&#10; &#13;&#10;";
	}
	return $input;
	#textArea({
	#	'name' => "note",
	#	'label' => "Log Notes",
	#	'value' => $input,
	#	'columns' => 2,
	#	'rows' => 1});
	#"<p style=\"height:50px\">$input</p>\n";
}

sub getMyOwnedGroups
{
	my $item = shift;
	my $table = "<table data-role=\"table\" data-mode=\"reflow\" class=\"ui-responsive\">\n";
        $table .= "<thead>\n";
        $table .= "<tr>\n";	
        $table .= "<th data-priority=\"1\">Name</th>\n";
        $table .= "<th data-priority=\"2\">Complete/Total</th>\n";
	$table .= "<th data-priority=\"3\">Action</th>\n";
        $table .= "</tr>\n";
        $table .= "</thead>\n";
	$table .= "<tbody>\n";
        my $hold = getAnySort(['SELECT * FROM itemgroups', 0,
                   [['n', 'itemid', $itemid]],
		   0]);
        my $ogroups;
	if ($hold->[1])
	{
		$ogroups = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}

	foreach my $ogroup (@{$ogroups})
	{
		$hold = getAnySort(["SELECT COUNT(*) as 'ccount' FROM groupitems g WHERE g.groupid = $ogroup->{'id'} AND EXISTS (SELECT * FROM item i WHERE i.id = g.itemid AND i.statusid = 2)", 0,
                   	              0,
				      0]);
                my $cgets;
	   	if ($hold->[1])
		{
			$cgets = $hold->[0];
		}else
		{
			return "NOPE: $hold->[2]: $hold->[3]\n";
		}

		$hold = getAnySort(["SELECT COUNT(*) as 'ccount' FROM groupitems g WHERE g.groupid = $ogroup->{'id'}", 0,
                   	              0,
				      0]);
                my $tgets;
	   	if ($hold->[1])
		{
			$tgets = $hold->[0];
		}else
		{
			return "NOPE: $hold->[2]: $hold->[3]\n";
		}

		$table .= "<tr>\n";		
		$table .= "<td>$ogroup->{'name'}</td>\n";
		$table .= "<td>$cgets->[0]{'ccount'}/$tgets->[0]{'ccount'}</td>\n";	
		$table .= "<td>\n";
		$table .= "<form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/task/itemgroup.cgi\" target=\"blank\">\n";
		$table .= "<input type=\"hidden\" name=\"groupid\" value=\"$ogroup->{'id'}\">\n";
		$table .= "<input type=\"submit\" name=\"submit\" value=\"View\">\n";		
		$table .= "</form>\n";
		$table .= "<form method=\"post\" onsubmit=\"return confirmDelete()\">\n";
		$table .= "<input type=\"hidden\" name=\"groupid\" value=\"$ogroup->{'id'}\">\n";
		$table .= "<input type=\"hidden\" name=\"itemid\" value=\"$item\">\n";
		$table .= "<input type=\"submit\" name=\"myremovegroup\" value=\"Delete\">\n";
		$table .= "</form>\n";
		#$table .= "<p>remove</p>\n";
		$table .= "</td>\n";
		$table .= "</tr>\n";

		
	}
	$table .= "</tbody></table>\n";
	return $table;
	
}

sub getMyGroups
{
	my $item = shift;
	my $table = "<table data-role=\"table\" data-mode=\"reflow\" class=\"ui-responsive\">\n";
        $table .= "<thead>\n";
        $table .= "<tr>\n";
        $table .= "<th data-priority=\"1\">Name</th>\n";
        $table .= "<th data-priority=\"2\">Highest Priority Completed/My Priority</th>\n";
        $table .= "<th data-priority=\"3\">View</th>\n";
        $table .= "</tr>\n";
        $table .= "</thead>\n";
	$table .= "<tbody>\n";
        my $hold = getAnySort(["SELECT * FROM itemgroups i WHERE EXISTS (SELECT * FROM groupitems g WHERE i.id = g.groupid AND g.itemid = $item)", 0,
                   0,
		   0]);
        my $ogroups;
	if ($hold->[1])
	{
		$ogroups = $hold->[0];
	}else
	{
		return "NOPE: $hold->[2]: $hold->[3]\n";
	}

	foreach my $ogroup (@{$ogroups})
	{
		$hold = getAnySort(["SELECT MAX(g.priority) as 'priority' FROM groupitems g WHERE g.groupid = $ogroup->{'id'} AND EXISTS (SELECT * FROM item i WHERE i.id = g.itemid AND i.statusid = 2)", 0,
                   	              0,
				      0]);
                my $cgets;
	   	if ($hold->[1])
		{
			$cgets = $hold->[0];
		}else
		{
			return "NOPE: $hold->[2]: $hold->[3]\n";
		}

		$hold = getAnySort(["SELECT priority FROM groupitems g WHERE g.groupid = $ogroup->{'id'} and g.itemid = $item", 0,
                   	              0,
				      0]);
                my $tgets;
	   	if ($hold->[1])
		{
			$tgets = $hold->[0];
		}else
		{
			return "NOPE: $hold->[2]: $hold->[3]\n";
		}

		$table .= "<tr>\n";
		$table .= "<td>$ogroup->{'name'}</td>\n";
		$table .= "<td>$cgets->[0]{'priority'}/$tgets->[0]{'priority'}</td>\n";
		$table .= "<td><form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/task/itemgroup.cgi\">\n";
		$table .= "<input type=\"hidden\" name=\"groupid\" value=\"$ogroup->{'id'}\">\n";
		$table .= "<input type=\"submit\" name=\"submit\" value=\"View\">\n";
		$table .= "</form></td>\n";
		$table .= "</tr>\n";

		
	}
	$table .= "</tbody></table>\n";
	return $table;
	
}

sub getMyItems
{
	my $item = shift;
	my $aitems;
	my $titem;
	my $table = "<table data-role=\"table\" data-mode=\"reflow\" class=\"ui-responsive\">\n";
        $table .= "<thead>\n";
        $table .= "<tr>\n";
        $table .= "<th data-priority=\"1\">Client</th>\n";
        $table .= "<th data-priority=\"2\">Name</th>\n";
        $table .= "<th data-priority=\"3\">Status</th>\n";
	$table .= "<th data-priority=\"4\">Creator</th>\n";
	$table .= "<th data-priority=\"5\">Action</th>\n";
        $table .= "</tr>\n";
        $table .= "</thead>\n";
	$table .= "<tbody>\n";
	my $hold = getAnySort(["SELECT aitemid 'item', bitemid 'myitem' FROM itemtoitem WHERE aitemid = $item UNION SELECT bitemid 'item', aitemid 'myitem' FROM itemtoitem WHERE bitemid = $item", 0,
                   0,
		   0]);
        if ($hold->[1])
	{
		$aitems = $hold->[0];
	}else
	{
		return  "NOPE: $hold->[2]: $hold->[3]\n";
	}

	foreach my $aitem (@{$aitems})
	{
		
		$hold = getAnySort(["SELECT i.name as 'itemname', c.name as 'clientname', ist.name as 'statusname', CONCAT(u.firstName, ' ', u.lastName) as 'username' FROM item i join clients c on i.clientid = c.id join itemstatus ist on i.statusid = ist.id join users u on i.userid = u.id WHERE i.id = $aitem->{'myitem'}", 0, 0, 0]);
		if ($hold->[1])
		{
			$titem = $hold->[0][0];
		}else
		{
			return "NOPE: $hold->[2]: $hold->[3]\n";
		}

		$table .= "<tr>\n";
		$table .= "<td>$titem->{'clientname'}</td>\n";
		$table .= "<td>$titem->{'itemname'}</td>\n";
		$table .= "<td>$titem->{'statusname'}</td>\n";
		$table .= "<td>$titem->{'username'}</td>\n";
		$table .= "<td>\n";
		$table .= "<a href=\"http://www.c2c-hit.net/c2cmobile/task/item.cgi?itemid=$aitem->{'myitem'}\" target=\"_blank\" class=\"ui-btn ui-corner-all\">View</a>\n";
		$table .= "<form method=\"post\">\n";
		$table .= "<input type=\"hidden\" name=\"removeitemid\" value=\"$aitem->{'myitem'}\">\n";
		$table .= "<input type=\"hidden\" name=\"itemid\" value=\"$item\">\n";
		$table .= "<input type=\"submit\" name=\"removeitem\" value=\"Delete\">\n";
		$table .= "</form></td>\n";
		
		$table .= "</tr>\n";

		
	}
	$table .= "</tbody></table>\n";
	return $table;
	
}



