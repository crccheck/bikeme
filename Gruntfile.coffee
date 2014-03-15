module.exports = (grunt) ->
  grunt.initConfig
    sass:
      dist:
        options:
          style: 'compressed'
          compass: true
        files: 'bikeme/apps/core/static/css/bikeme.css': 'bikeme/apps/core/static/sass/bikeme.sass'

    watch:
      options:
        livereload: true
      sass:
        files: 'bikeme/apps/core/static/sass/*.s?ss'
        tasks: ["sass", ]

  grunt.loadNpmTasks 'grunt-contrib-sass'
  grunt.loadNpmTasks 'grunt-contrib-watch'

  grunt.registerTask 'default', ['sass']
  grunt.registerTask 'dev', ['default', 'watch']
