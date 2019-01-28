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
use itemDatabase qw(:Groupitems :Display :Tags :Item :Itemtag);
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
my $client;
my $tagdefault;
my $itemlist;
my @items;
my @elements;
my $time;
my @tags;
my $message = "";
my $iteminfo;
my $itemid;
my $allitems;
my $hold;

my $groupid;
my @allids;

my $additemresult;
my $addtagresult;
my $itemadd = 0;

#test form values and untaint
$groupid = $cgi->param('groupid');


if ($cgi->param('add') )
{    
    $itemadd = 1;
    $client = $cgi->param('client');
    $tagdefault = $cgi->param('tagdefault');
    $itemlist = $cgi->param('itemlist');
    @items = split /\n/, $itemlist;
    my ($year,$month,$day, $hour,$min,$sec) = Today_and_Now();
    $time = "$year-$month-$day $hour:$min:$sec";
    undef $additemresult;
    if ($client)
    {
	foreach my $item (@items)
	{
	    @elements = split /,/, $item;

	    if (@elements == 2)
	    {
		$additemresult = addEditItem([$userid, 0, {name => $elements[0], description => $elements[1], clientid => $client, createdate => $time, lasteditdate => $time, statusid => 1}]);
	    }elsif (@elements == 3)
	    {
		$additemresult = addEditItem([$userid, 0, {name => $elements[0], description => $elements[1], clientid => $client, createdate => $time, lasteditdate => $time, statusid => 1, startdate => $elements[2]}]);
	    }elsif (@elements == 4)
	    {
		$additemresult = addEditItem([$userid, 0, {name => $elements[0], description => $elements[1], clientid => $client, createdate => $time, lasteditdate => $time, statusid => 1, startdate => $elements[2], enddate => $elements[3]}]);
	    }
	    
	    
	    if ($additemresult->[0])
	    {
		$iteminfo = getAnySort["SELECT MAX(id) as 'id' from item WHERE userid = $userid AND createdate = '$time'", 0, 0, 0];
		$itemid = $iteminfo->[0][0]{'id'};
		$addtagresult = addItemTags([$itemid, [$tagdefault], $userid]);

		push @allids, $itemid;
	    }else
	    {
		$message .= "Item not added: $elements[0]";
	    }
	    
	}

	if ($groupid)
	{
	    $hold = addEditGroupItems([$userid, $groupid, \@allids, 0]);
	}

    }else
    {
	$message = "You must pick a client.";
    }
	 
}


#HTML with FORM

print $cgi->header();
print jqheader();

print "<div data-role=\"page\">\n";
print jqpageheader("C2C Task", 1, $userrights);
#print jqnavbar($userrights);
print "</div>\n";

print "<div data-role=\"main\" class=\"ui-content\">\n";

print "$message";

if ($itemadd)
{
    $allitems = getAnySort(["SELECT iic.name as 'client', iis.name as 'status', ig.name as 'type', i.id as 'itemid', i.name as 'name', i.description, i.clientid, i.startdate, i.enddate, i.createdate, i.lasteditdate, i.statusid, i.userid as 'owner' FROM item i join itemtag ig on EXISTS (SELECT * FROM itemtotag itg WHERE i.id = itg.itemid AND ig.id = itg.tagid AND tagdefault = 1) join itemstatus iis on i.statusid = iis.id join clients iic on i.clientid = iic.id WHERE i.userid = $userid AND i.createdate = '$time'", 0, 0, 0]);

    print "<p>These Items were added.</p>\n";
    
    print "<form method=\"post\">\n";
   
    my $notadded;
    foreach my $item (@{$allitems->[0]})
    {
	print itemDisplay($item, 1); #item, editable, group
	#print "ITEMID::  $item->{'itemid'}\n";
	
    }
    print "<br>\n";
    
    print "</form>\n";
}else
{

    if ($userrights > 1)
    {
	print "<p>To add items you must pick a client, enter a name, and enter a description. You can also set the start datetime and end datetime. The following formats are accepted for each row or item:</p>\n";
	print "<ul>\n";
	print "<li>name,description</li>\n";
	print "<li>name,description,start datetime</li>\n";
	print "<li>name,description,start datetime, end datetime</li>\n";
	print "</ul>\n";
	print "<p>The following formats are accepted for the datetimes you may add:</p>\n";
	print "<ul>\n";
	print "<li>yyyy-mm-dd (yy-m-d)</li>\n";
	print "<li>yyyy-mm-dd hh:mm:ss</li>\n";
	print "</ul>\n";
	print "<form method=\"post\">\n";

	if ($groupid)
	{
	    print "<input type=\"hidden\" name=\"groupid\" value=\"$groupid\">\n";
	}

	print getMyTags(1, 'Type', 'tagdefault', 0);
	print getMyClients();
	print textArea({name => 'itemlist', label => 'Item List', value => ""});
	if ($groupid)
	{
	    print "<input type=\"submit\" name=\"add\" value=\"Add To Group\">\n";
	}else
	{
	    print "<input type=\"submit\" name=\"add\" value=\"Add\">\n";
	}
	#getDescription
	print "</form>\n";
    }
}




print "</div>\n";




print jqpagefooter("Coast to Coast Innovative Solutions");
print "</div>\n";

print $cgi->end_html();


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


