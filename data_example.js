var stdin = process.stdin;
var mongoose = require('mongoose'),
	  Schema = mongoose.Schema;

//Modify default: 'A' changing the letter execution per execution
var BoardSchema = new Schema({
	type	: { type: Number, validate: /[0|1]/, default: 1 },
	value	: { type: String, default: 'A'},
	x			: { type: Number, default: 10 },
	y			: { type: Number, default: 10 }
});

var db = mongoose.connect('mongodb://localhost/blackboard');
var model = mongoose.model('Data', BoardSchema);

var Data = mongoose.model('Data');

	var i=0;
	for(i;i<1000;i++) {
		var data = new Data();
		data.type = 0;	//
		data.value = "0" + Math.floor((Math.random()*6)+1); // data.value = "01";	// Client will pull "img/objects/img01.png"
		console.log('value = '+data.value)
		data.x=Math.ceil(Math.random()*1000);
		data.y=Math.ceil(Math.random()*1000);
		data.save(function(err) {
			if(err) { throw err; }
			console.log('saved');
		});
	}

/*data.save(function(err){
	if(err) { throw err; }
	console.log('saved');
	Data.find({value: 'B'}, function(err, docs) {
		if(err) { throw err; }
		docs.forEach(function(doc){
			console.log(doc);
		});
		mongoose.disconnect();
	});
});*/
