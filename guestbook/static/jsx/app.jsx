/** @jsx React.DOM */

// The main "hero unit" title and subtitle for the page
var HeroComponent = React.createClass({
    render: function() {
        return (
            <div className="hero">
                <h1>{this.props.title}</h1>
                <h2>{this.props.subtitle}</h2>
            </div>);
    }
});

// Holds the announcement text directly as its innerHTML
var AnnouncementComponent = React.createClass({
    render: function() {
        return (
            <p className="announcement" dangerouslySetInnerHTML={{__html: this.props.announcement}} />
        );
    }
});

// Holds the list of attendees
var GuestListComponent = React.createClass({
    render: function() {
        var guestEntries = this.props.guests.map(function(guest) {
            return <GuestEntryComponent
                key={guest.id}
                id={guest.id}
                name={guest.name}
                twitter_handle={guest.twitter_handle}
                signed_up_at={guest.signed_up_at} />
        });
        return (
            <ul className="guest-list pure-u-12-24">
              {guestEntries}
            </ul>
        );
    }
});

// Represents a single attendee
var GuestEntryComponent = React.createClass({
    render: function() {
        var signupDate = moment(this.props.signed_up_at);
        var twitterURL = "http://twitter.com/" + this.props.twitter_handle;
        return (
            <li id="guest-{this.props.id}">
              <span className="guest-signed-up-at">{signupDate.fromNow()}</span>
              <span className="guest-name">{this.props.name}</span>
              <span className="guest-twitter">
                <a href={twitterURL}>{this.props.twitter_handle}</a>
              </span>
            </li>);
    }
});

// Where new guests sign up
var GuestSignupFormComponent = React.createClass({
    handleSubmit: function(e) {
        e.preventDefault();
        // Get the values
        var name = this.refs.name.getDOMNode().value.trim();
        var twitter = this.refs.twitter.getDOMNode().value.trim();
        // Call the higher-level callback which will update our props
        this.props.onSignup({name: name, twitter_handle: twitter});
        // Clear the form
        this.refs.name.getDOMNode().value = '';
        this.refs.twitter.getDOMNode().value = '';
    },
    render: function() {
        return (
            <form method="post" className="signup-form pure-form pure-form-stacked" onSubmit={this.handleSubmit}>
              <fieldset>
              <div className="pure-control-group">
                <label htmlFor="signup-name">name</label>
                <input type="text" placeholder="your name" ref="name" id="signup-name"/>
              </div>
              <div className="pure-control-group">
                <label htmlFor="signup-twitter">twitter</label>
                <input type="text" placeholder="@you" ref="twitter" id="signup-twitter"/>
              </div>
              <div className="pure-controls">
                <button type="submit" className="pure-button pure-button-primary">I&rsquo;ll be there!</button>
              </div>
              </fieldset>
            </form>
        );
  }
});

var LoadingNotificationComponent = React.createClass({
    render: function() {
        var classSet = React.addons.classSet;
        var classes = classSet({
            "loading-notification": true,
            "loading-pending": (this.props.status == "pending"),
            "loading-success": (this.props.status == "success"),
            "loading-error": (this.props.status == "error"),
            "hidden": (!this.props.visible)
        });
        return (
            <div className={classes}>{this.props.text}</div>
        );
    }
});


// Contains all the other components -- housed in the #main DIV
var MainComponent = React.createClass({
    handleSignup: function(signup) {
        signup.signed_up_at = (new Date()).toISOString();
        signup.id = (new Date()).getTime();
        var originalGuests = this.state.guests.slice();
        var updatedGuests = originalGuests.concat([signup])
        this.setState({
            guests: updatedGuests,
            loadingState: {
                visible: true,
                text: "loading...",
                status: "pending"
            }
        });
        // Using the qwest micro-library
        console.log("TRYING TO SEND", JSON.stringify(signup));
        reqwest({
            url: "/signup",
            method: "POST",
            type: "json",
            contentType: "application/json",
            data: JSON.stringify(signup),
            success: function(res) {
                this.setState({
                    guests: res.guests || [],
                    loadingState: {
                        visible: true,
                        text: "success!",
                        status: "success"
                    }
                });
                setTimeout(function() {
                    this.setState({
                        loadingState: {
                            visible: false,
                            text: "",
                            status: null
                        }
                    });
                }.bind(this), 2000);
              }.bind(this),
            error: function(err) {
                console.log("error, reverting to", originalGuests);
                console.error(err.toString());
                this.setState({
                    guests: originalGuests || [],
                    loadingState: {
                        visible: true,
                        text: "please try again",
                        status: "error"
                    }
                });
                setTimeout(function() {
                    this.setState({
                        loadingState: {
                            visible: false,
                            text: "",
                            status: null
                        }
                    });
                }.bind(this), 2000);
              }.bind(this)
        });
    },
    getInitialState: function() {
        return {
            guests: this.props.guests || [],
            loadingState: {
                visible: false,
                text: "",
                status: null
            }
        };
    },
    render: function() {
        return (
            <div className="center-container">
              <HeroComponent title={this.props.title} subtitle={this.props.subtitle} />
              <AnnouncementComponent announcement={this.props.announcement} />
              <div className="pure-g">
                <div className="pure-u-11-24">
                  <GuestSignupFormComponent onSignup={this.handleSignup} />
                  <LoadingNotificationComponent ref="loading"
                      visible={this.state.loadingState.visible}
                      text={this.state.loadingState.text}
                      status={this.state.loadingState.status} />
                </div>
                <GuestListComponent guests={this.state.guests}/>
              </div>
            </div>
        );
    }
});
