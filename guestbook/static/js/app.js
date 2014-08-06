/** @jsx React.DOM */

// The main "hero unit" title and subtitle for the page
var HeroComponent = React.createClass({displayName: 'HeroComponent',
    render: function() {
        return (
            React.DOM.div({className: "hero"}, 
                React.DOM.h1(null, this.props.title), 
                React.DOM.h2(null, this.props.subtitle)
            ));
    }
});

// Holds the announcement text directly as its innerHTML
var AnnouncementComponent = React.createClass({displayName: 'AnnouncementComponent',
    render: function() {
        return (
            React.DOM.p({className: "announcement", dangerouslySetInnerHTML: {__html: this.props.announcement}})
        );
    }
});

// Holds the list of attendees
var GuestListComponent = React.createClass({displayName: 'GuestListComponent',
    render: function() {
        var guestEntries = this.props.guests.map(function(guest) {
            return GuestEntryComponent({
                key: guest.id, 
                id: guest.id, 
                name: guest.name, 
                twitter_handle: guest.twitter_handle, 
                signed_up_at: guest.signed_up_at})
        });
        return (
            React.DOM.ul({className: "guest-list pure-u-12-24"}, 
              guestEntries
            )
        );
    }
});

// Represents a single attendee
var GuestEntryComponent = React.createClass({displayName: 'GuestEntryComponent',
    render: function() {
        var signupDate = moment(this.props.signed_up_at);
        var twitterURL = "http://twitter.com/" + this.props.twitter_handle;
        return (
            React.DOM.li({id: "guest-{this.props.id}"}, 
              React.DOM.span({className: "guest-signed-up-at"}, signupDate.fromNow()), 
              React.DOM.span({className: "guest-name"}, this.props.name), 
              React.DOM.span({className: "guest-twitter"}, 
                React.DOM.a({href: twitterURL}, this.props.twitter_handle)
              )
            ));
    }
});

// Where new guests sign up
var GuestSignupFormComponent = React.createClass({displayName: 'GuestSignupFormComponent',
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
            React.DOM.form({method: "post", className: "signup-form pure-form pure-form-stacked", onSubmit: this.handleSubmit}, 
              React.DOM.fieldset(null, 
              React.DOM.div({className: "pure-control-group"}, 
                React.DOM.label({htmlFor: "signup-name"}, "name"), 
                React.DOM.input({type: "text", placeholder: "your name", ref: "name", id: "signup-name"})
              ), 
              React.DOM.div({className: "pure-control-group"}, 
                React.DOM.label({htmlFor: "signup-twitter"}, "twitter"), 
                React.DOM.input({type: "text", placeholder: "@you", ref: "twitter", id: "signup-twitter"})
              ), 
              React.DOM.div({className: "pure-controls"}, 
                React.DOM.button({type: "submit", className: "pure-button pure-button-primary"}, "I’ll be there!")
              )
              )
            )
        );
  }
});

var LoadingNotificationComponent = React.createClass({displayName: 'LoadingNotificationComponent',
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
            React.DOM.div({className: classes}, this.props.text)
        );
    }
});


// Contains all the other components -- housed in the #main DIV
var MainComponent = React.createClass({displayName: 'MainComponent',
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
            React.DOM.div({className: "center-container"}, 
              HeroComponent({title: this.props.title, subtitle: this.props.subtitle}), 
              AnnouncementComponent({announcement: this.props.announcement}), 
              React.DOM.div({className: "pure-g"}, 
                React.DOM.div({className: "pure-u-11-24"}, 
                  GuestSignupFormComponent({onSignup: this.handleSignup}), 
                  LoadingNotificationComponent({ref: "loading", 
                      visible: this.state.loadingState.visible, 
                      text: this.state.loadingState.text, 
                      status: this.state.loadingState.status})
                ), 
                GuestListComponent({guests: this.state.guests})
              )
            )
        );
    }
});
