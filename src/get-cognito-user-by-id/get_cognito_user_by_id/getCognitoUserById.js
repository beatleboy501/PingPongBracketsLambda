var AWS = require('aws-sdk');

exports.handler = async (event) => {
    const users = await getUsers(event)
    const response = {
        statusCode: 200,
        headers: {
            "Access-Control-Allow-Origin": "*"
        },
        body: JSON.stringify(users),
    };
    return response;
};

function getUsers(event) {
    var sub = event.id
    var params = {
    	  UserPoolId: 'us-east-1_AorlPKW44',
    	  AttributesToGet: ['sub', 'email', 'given_name', 'family_name'],
    	  Filter: "sub=\"" + sub + "\""
    	};

    	return new Promise((resolve, reject) => {
    		AWS.config.update({ region: 'us-east-1', 'accessKeyId': process.env.AWS_ACCESS_KEY_ID, 'secretAccessKey': process.env.AWS_SECRET_KEY });
    		var cognitoidentityserviceprovider = new AWS.CognitoIdentityServiceProvider();
    		cognitoidentityserviceprovider.listUsers(params, (err, data) => {
    			if (err) {
    				console.log(err);
    				reject(err)
    			}
    			else {
    			    var success = data.Users.map(user => {
    			        var userAttributes = user.Attributes.map(attribute => {
    			            var attrKey = attribute.Name;
    			            var attrValue = attribute.Value;
    			            var attrObj = {};
    			            attrObj[attrKey] = attrValue;
    			            return attrObj;
    			        });
    			        return Object.assign(...userAttributes);
    			    })[0
    				console.log("data", success);
    				resolve(success)
    			}
    		})
    	});
}
