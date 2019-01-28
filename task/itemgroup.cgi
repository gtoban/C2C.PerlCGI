#!/usr/bin/perl
use cPanelUserConfig;
use strict;
use warnings;

use Date::Calc qw(Days_in_Month Today_and_Now);
use DBI;
use CGI::Session;
use CGI;
use lib '/home/c2cmedical/public_html/c2c/modules';
use Manager qw(:User :Usercheck);
use htmlManager qw(:elements);
use itemDatabase qw (:Item :Tags :Itemgroups :Itemtag :Itemuser :Groupitems);
use clientManager qw (:Client);
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
my $groupid;
my $group;
my $creator;
my $hold;
my $creatoruser;
my $creatorclient;
my $items;
my $readonly = 0;
my $itemreadonly = 0;
my $itemnotdeleted = 1;
my $message = "";

my $name;# = $cgi->param('name');
my $description;# = $cgi->param('description');
my $go;# = 1;
my $itemid;


#test form values and untaint
$groupid = $cgi->param('groupid');

if ($cgi->param('deletegroup'))
{
    $hold = deleteItemGroups([$groupid, $userid]);
    if ($hold->[1])
    {
	$message .= "Group Deleted";
	$itemnotdeleted = 0;
    }else
    {
	$message .= "ERROR: $hold->[2]: $hold->[3]\n";
    }
    
}
if ($cgi->param('editgroup'))
{
    $name = $cgi->param('name');
    $description = $cgi->param('description');
    
    $hold = addItemGroups([$groupid, $userid, {description => $description, name => $name}]);

    $message = $hold->[2];
       
     
}
if ($cgi->param('addnew'))
{
    my $type = $cgi->param('tagdefault');
    my $client = $cgi->param('client');
    $name = $cgi->param('name');
    $description = $cgi->param('description');
    my @tag = $cgi->param('tag');
    my @users = $cgi->param('users');
    my $startyear = $cgi->param('yearstart');
    my $startmonth = $cgi->param('monthstart');
    my $startday = $cgi->param('daystart');
    my $starthour = $cgi->param('hourstart');
    my $startmin = $cgi->param('startmin');
    my $endyear = $cgi->param('yearend');
    my $endmonth = $cgi->param('monthend');
    my $endday = $cgi->param('dayend');
    my $endhour = $cgi->param('hourend');
    my $endmin = $cgi->param('endmin');
    my $startdate = "$startyear-$startmonth-$startday $starthour:$startmin:00";
    my $enddate = "$endyear-$endmonth-$endday $endhour:$endmin:00";
    my ($year,$month,$day, $hour,$min,$sec) = Today_and_Now();
    my $time = "$year-$month-$day $hour:$min:$sec";
    
    $hold = addEditItem([$userid, 0, {name => $name, description => $description, clientid => $client, startdate => $startdate, enddate => $enddate, createdate => $time, lasteditdate => $time, statusid => 1}]);

    $message .= $hold->[1];

    $hold = getAnySort(["SELECT * FROM item WHERE userid = $userid AND createdate = '$time'", 0, 0, 0]);
    $itemid = $hold->[0][0]{'id'};
    push @tag, $type;
    $hold = addItemTags([$itemid, \@tag, $userid]);
    $hold = addItemUser([$itemid, \@users, $userid]);
    $hold = addEditGroupItems([$userid, $groupid, [$itemid]]);
    $message .= $hold->[1];
	
}
if ($cgi->param('updateitems'))
{
    if ($userrights == 3)
    {
	$hold = getAnySort(["SELECT * FROM groupitems WHERE groupid = $groupid", 0, 0, 0]);
    }else
    {
	$hold = getAnySort(["SELECT * FROM groupitems gi WHERE gi.groupid = $groupid AND EXISTS (SELECT * FROM item i WHERE gi.itemid = i.id AND i.userid = $userid) UNION SELECT * FROM groupitems gi WHERE gi.groupid = $groupid AND EXISTS (SELECT * FROM itemtouser itu WHERE gi.itemid = itu.itemid AND itu.userid = $userid)", 0, 0, 0]);
    }
    my $ids = $hold->[0];
    #$message = "MESSAGE: $ids->[0]{'id'}";
    my $status;
    my $priority;
    my $id;
    foreach my $itemids (@{$ids})
    {
	$id = $itemids->{'itemid'};
	$status = $cgi->param("$id.status");
	$priority = $cgi->param("$id.priority");
	$hold = getAnySort(["SELECT * FROM item WHERE id = $id AND statusid = $status", 0, 0, 0]);
	#$message .= "$hold->[2] : $hold->[3] : $id.status  :";
	if (!$hold->[0])
	{
	    $hold = addEditItem([$userid, $id, {statusid => $status}]);
	    $message .= $hold->[1];
	}
	$hold = getAnySort(["SELECT * FROM groupitems WHERE itemid = $id AND groupid = $groupid AND priority = $priority", 0, 0, 0]);
	
	if (!$hold->[0])
	{
	    $hold = addEditGroupItems([$userid, $groupid, {itemid => $id, priority => $priority}, 1]);
	    $message .= "$hold->[2] : $hold->[3] : $id.priority  :";
	}
	
    }
}
 

$group = getAnySort(["SELECT * FROM itemgroups WHERE id = $groupid", 0, 0, 0]);
$creator = getAnySort(["SELECT * FROM item WHERE id = $group->[0][0]{'itemid'}" ,0 ,0 ,0]);
$hold = getAnySort(["SELECT * FROM users WHERE id = $creator->[0][0]{'userid'}", 0, 0, 0]);
$creatoruser = "$hold->[0][0]{'firstName'} $hold->[0][0]{'lastName'}";
$hold = getAnySort(["SELECT * FROM clients WHERE id = $creator->[0][0]{'clientid'}", 0, 0, 0]);
$creatorclient = "$hold->[0][0]{'name'}";
$items = getAnySort(["SELECT gi.id, i.id as 'itemid', itg.name as 'type', c.name as 'client', i.name as 'item', its.id as 'statusid', its.name as 'status', gi.priority FROM item i JOIN groupitems gi on i.id = gi.itemid JOIN clients c on i.clientid = c.id JOIN itemstatus its on i.statusid = its.id JOIN itemtag itg on EXISTS (SELECT * FROM itemtotag itt WHERE i.id = itt.itemid AND itt.tagid = itg.id) AND itg.tagdefault = 1 WHERE gi.groupid = $groupid", 0, 0, 0]);

if($userid == $creator->[0][0]{'userid'} || $userrights == 3)
{
    $readonly = 1;
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
print jqpageheader("C2C Group", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

# Creator
# view
# creator client name 
# Gen Info
# delete
# name description
# Items (if creator or admin)addnew
# name description priority (if creator or admin )edit (if item owner or assigned or admin)view (if creator or admin)remove
# (if creator)edit

print "<h1>Creator</h1>\n";
print "<form method=\"POST\" action=\"http://www.c2c-hit.net/c2cmobile/task/item.cgi\">\n";
print "<input type=\"hidden\" name=\"itemid\" value=\"$creator->[0][0]{'id'}\">\n";
print "<input type=\"submit\" value=\"View\">\n";
print "</form>\n";
print "<div class=\"ui-grid-b\">\n";
print "<div class=\"ui-block-a\">\n";
print "<p>Creator User Name</p>\n";
print "<p>$creatoruser</p>\n";
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print "<p>Creator Client Name</p>\n";
print "<p>$creatorclient</p>\n";
print "</div>\n";
print "<div class=\"ui-block-c\">\n";
print "<p>Creator Item Name</p>\n";
print "<p>$creator->[0][0]{'name'}</p>\n";
print "</div>\n";
print "</div>\n";

print "<h1>Group Gen Info</h1>\n";
if ($readonly)
{
    print "<form method=\"POST\">\n";
    print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
    print "<input type=\"submit\" name=\"deletegroup\" value=\"Delete\" onsubmit=\"return confirmDelete()\">\n";
    print "</form>\n";
}
print "<form method=\"POST\">\n";
print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print textInput({name => "name", label => "Name", value => $group->[0][0]{'name'}});
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print textArea({name => "description", label => "Description", value => $group->[0][0]{'description'}});
print "</div>\n";
print "</div>\n";
if ($readonly)
{
    print "<input type=\"submit\" name=\"editgroup\" value=\"Edit\">\n";

}
print "</form>\n";

print "<h1>Add Items</h1>\n";
print "<form method=\"POST\" action=\"http://www.c2c-hit.net/c2cmobile/task/itemsearch.cgi\" target=\"_blank\">\n";
print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
print "<input type=\"submit\" name=\"addexist\" value=\"Add Existing\">";
print "</form>\n";


print "<form method=\"post\">\n";
print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print getMyTags(1, 'Type', 'tagdefault', 0);
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print getMyClients();
print "</div>\n";
print "</div>\n";
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print textInput({'name' => 'name', 'label' => 'Name'});
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print textArea({'name' => 'description', 'label' => 'Description'});
print "</div>\n";
print "</div>\n";
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print getMyTags(0, 'Tags', 'tag', 1);
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print getMyUsers();
print "</div>\n";
print "</div>\n";
print "<div class=\"ui-grid-a\">\n";
print "<div class=\"ui-block-a\">\n";
print datetimepicker("start", 0, 0, 0, 0, 0, 1);
print "</div>\n";
print "<div class=\"ui-block-b\">\n";
print datetimepicker("end", 0, 0, 0, 0, 0, 1);
print "</div>\n";
print "</div>\n";
print "<input type=\"submit\" name=\"addnew\" value=\"Add New\">";
#getDescription
print "</form>\n";
print "<form method=\"POST\" action=\"http://www.c2c-hit.net/c2cmobile/task/addmanyitems.cgi\" target=\"_blank\">\n";
print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
print "<input type=\"submit\" name=\"submit\" value=\"Add Many New\">";
print "</form>\n";
print "</div>\n";

print "<h1>Items</h1>\n";
my $table = "";
my %options;
my %statuses;
my $hiddenids = "";
my $assigned;
my $i = 0;
if (@{$items->[0]})    
{
    $i = 1;
    while ($i <= @{$items->[0]})
    {
	$options{$i} = $i;
	$i += 1;
    }
    $hold = getAnySort(["SELECT * FROM itemstatus", 0, 0, 0]);
    $i = 0;
    while ($i < @{$hold->[0]})
    {
	$statuses{$hold->[0][$i]{'id'}} = $hold->[0][$i]{'name'};
	$i += 1;
    }
    
    $table .= "<form method=\"POST\">\n";
    $table .= "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
    $table .= "<table data-role=\"table\" data-mode=\"reflow\" class=\"ui-responsive\">\n";
    $table .= "<thead>\n";
    $table .= "<tr>\n";
    $table .= "<th data-priority=\"1\">Type</th>\n";
    $table .= "<th data-priority=\"2\">Client</th>\n";
    $table .= "<th data-priority=\"3\">Name</th>\n";
    $table .= "<th data-priority=\"4\">Status</th>\n";
    $table .= "<th data-priority=\"5\">Priority</th>\n";
    
    $table .= "</tr>\n";
    $table .= "</thead>\n";
    $table .= "<tbody>\n";
    $i = 0;
    foreach my $item (@{$items->[0]})
    {
	$itemreadonly = 0;
	$assigned = getAnySort(["SELECT * FROM itemtouser WHERE itemid = $item->{'itemid'} AND userid = $userid", 0, 0, 0]);
	if ($assigned->[0] || $userrights == 3)
	{
	    $itemreadonly = 1;
	}
	$table .= "<input type=\"hidden\" name=\"id[$i]\" value=\"$item->{'id'}\">\n";
	$i += 1;
	$table .= "<tr>\n";
	$table .= "<td><p>$item->{'type'}</p></td>\n";
	$table .= "<td><p>$item->{'client'}</p></td>\n";
	$table .= "<td><p><a href=\"http://www.c2c-hit.net/c2cmobile/task/item.cgi?itemid=$item->{'itemid'}\" target=\"_blank\">$item->{'item'}</a></p></td>\n";
	if ($itemreadonly)
	{
	    $table .= "<td>\n";	
	    $table .= selectList({
		'blankoption' => 0,
		'multiple' => 0,
		'options' => \%statuses,
		'selected' => [$item->{'statusid'}],
		'name' => "$item->{'itemid'}.status",
		'label' => 'Status',
		'hiddenlabel' => 1
				 });
	    $table .= "</td>\n";
	}else
	{
	    $table .= "<td><p>$item->{'status'}</p></td>\n";
	}
	if ($readonly)
	{
	    $table .= "<td>\n";	
	    $table .= selectList({
		'blankoption' => 1,
		'multiple' => 0,
		'options' => \%options,
		'selected' => [$item->{'priority'}],
		'name' => "$item->{'itemid'}.priority",
		'label' => 'Priority',
		'hiddenlabel' => 1
				 });
	    $table .= "</td>\n";
	    
	}else
	{
	    
	    $table .= "<td><p>$item->{'priority'}</p></td>\n";
	}
	$table .= "</tr>\n";
    }
    $table .= "</body></table>\n";
    #$table .= $hiddenids;
    $table .= "<input type=\"submit\" name=\"updateitems\" value=\"Update\">\n";
    $table .= "</form>\n";
    print $table;
    
}

if ($message)
{
    print "<script> alert(\"$message\")</script>";
}

print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();

sub mycreator
{
    return 1 if($userid == $creator->[0][0]{'userid'} || $userrights == 3);
    return 0;
}

sub myowner
{
    my $titemid = shift;
    my $assigned = getAnySort(["SELECT * FROM itemtouser WHERE itemid = $titemid AND userid = $userid", 0, 0, 0]);
    if ($assigned->[0][0] || $userrights == 3)
    {
	return 1;
    }

    return 0;
}

sub getMyClients
{
	my @clients = getClients();
	my %clienthash;
	foreach my $client (@clients)
	{
		$clienthash{"$client->{'clientid'}"} = $client->{'name'};
	}
	my $info = {
	      'blankoption' => 1,
	      'multiple' => 0,
	      'options' => \%clienthash,
	      'name' => 'client',
	      'label' => 'Client'
	};

	return selectList($info);
	      
	
}

sub getMyTags
{
	my $default = shift;
	my $label = shift;
	my $name = shift;
	my $multiple = shift;
	my $options;
	my $taginfo = getTags({ 'default' => $default});
	my $tags = $taginfo->[0];
	foreach my $tag (@{$tags})
	{
		if ($tag->{'id'} != 1 && $tag->{'tagdefault'} == $default)
		{
			$options->{$tag->{'id'}} = $tag->{'name'};
		}
	}
	my $info = {
	      'blankoption' => 0,
	      'multiple' => $multiple,
	      'options' => $options,
	      'name' => $name,
	      'label' => $label
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
	my $myusers;
	my $users;
	my %options;
	my $count;
	

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
	      'name' => 'users',
	      'label' => 'Associated People'
	};

	return selectList($info);
	
}

