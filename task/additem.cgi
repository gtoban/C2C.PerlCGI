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
use itemDatabase qw(:Tags :Item :Itemtag);
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
my $name;
my $description;
my $time;
my @tags;
my $newtag;
my $message = "";
my $iteminfo;
my $items;
my $item;
my $itemid;
my $itemwasadded = 0;

my $newtagname;
my $additemresult;
my $addtagresult;

#test form values and untaint

if ($cgi->param('add') )
{
	my $go = 1;
	$client = $cgi->param('client');
	$tagdefault = $cgi->param('tagdefault');
	$name = $cgi->param('name');
	$description = $cgi->param('description');
	if (!checkTheseWords($name))
	{
		$go = 0;
		$message = "Bad Name";
	}
	if (!checkTheseWords($description))
	{
		$go = 0;
		$message = "Bad Description";
	}
	if ($go)
	{
	@tags = $cgi->param('tag');
	my ($year,$month,$day, $hour,$min,$sec) = Today_and_Now();
	$time = "$year-$month-$day $hour:$min:$sec";
	#Type, column name, value

	$additemresult = addEditItem([$userid, 0, {name => $name, description => $description, clientid => $client, createdate => $time, lasteditdate => $time, statusid => 1}]);
	 if ($additemresult->[0])
	 {	    
		$itemwasadded = 1;
		$iteminfo = getAny(['item', 0, ['d', 'createdate', $time], [0, 'userid', $userid]]);
		#$items = $iteminfo[0];
		if ($iteminfo->[1])
		{			
			$items = $iteminfo->[0];
			$itemid = $items->[0]{'id'};
			unshift @tags, $tagdefault;
			$message = "Good Item";
			$addtagresult = addItemTags([$itemid, \@tags, $userid]);
			
		        if ($addtagresult->[0])
		        {
		        	$message .= ": Good TagD";
		        }else
		        {
		        	$message .= ": Bad TagD; $addtagresult->[1]";
		        }
			
		}else
		{
			$message = "NOPE: $iteminfo->[2] : $iteminfo->[3]";
		}
	 }else
	 {
		$message = "NOPE: $additemresult->[1] : $additemresult->[2]";
	 }
	 
	 
	 }
	 
}elsif ($cgi->param('addtag'))
{
	$newtagname = $cgi->param('addtag');
	if (checkName($newtagname))
	{
		my $newtagresult = addUpdate(['itemtag',
				     [1, 'name', $newtagname],
				     [0, 'tagdefault', 0],
				     [0, 'active', 1]]);
		if ($newtagresult->[0])
		{
			$message = "Tag Added";
		}else
		{
			$message = "Tag NOT Added: $newtagresult->[1]: $newtagresult->[2]";
		}
		
	}else
	{
		$message = "Bad Tag Name : $newtagname";
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

if ($itemwasadded)
{
print "<form method=\"post\" action=\"http://www.c2c-hit.net/c2cmobile/task/item.cgi\">\n";
print "<input type=\"hidden\" name=\"itemid\" value=\"$itemid\" >\n";
print "<input type=\"submit\" name=\"submit\" value=\"Go To Item\">";
#getDescription
print "</form>\n";
}else
{

if ($userrights > 1)
{

print "<form method=\"post\">\n";

print getMyTags(1, 'Type', 'tagdefault', 0);
print getMyClients();
print textInput({'name' => 'name', 'label' => 'Name'});
print textArea({'name' => 'description', 'label' => 'Description'});
print "<div class=\"ui-grid-b\">\n";
print "<div class=\"ui-block-a\">\n";
print getMyTags(0, 'Tags', 'tag', 1);
print "</div>";
print "<div class=\"ui-block-b\">\n";
print textInput({'name' => 'addtag', 'label' => 'Add Tag'});
print "</div>\n";
print "<div class=\"ui-block-c\">\n";
print "<button type=\"submit\" name=\"newtag\" class=\"ui-btn ui-shadow ui-corner-all ui-btn-icon-notext ui-icon-plus\"></button>";
print "</div>\n";
print "</div>\n";
print "<input type=\"submit\" name=\"add\" value=\"Add\">";
#getDescription
print "</form>\n";
}else
{
print "<h1>Ticket</h1>\n";
print "<form method=\"post\">\n";

print "<input type=\"hidden\" name=\"tagdefault\" value=\"1\" >\n";
print "<input type=\"hidden\" name=\"client\" value=\"$userclientid\" >\n";
print textInput({'name' => 'name', 'label' => 'Name'});
print textArea({'name' => 'description', 'label' => 'Description'});
print getMyTags(0, 'Tags', 'tag', 1);
print "<input type=\"submit\" name=\"add\" value=\"Add\">";
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


